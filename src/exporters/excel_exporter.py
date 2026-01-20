"""Exportador de datos de groove a Excel."""
from typing import Dict, List, Optional
from pathlib import Path

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

from ..models import (
    GrooveData, InstrumentData, GridMapping,
    HumanizationStats, SwingAnalysis, JamaicanStyle
)


class ExcelExporter:
    """
    Exporta datos de groove a formato Excel.

    Genera dos hojas:
    - REJILLAS: Patrones de grid (0/1) por instrumento
    - HUMANIZACION: Velocidades y desviaciones de timing

    Formato compatible con DAWs y herramientas de produccion.
    """

    def __init__(self):
        if not HAS_OPENPYXL:
            raise ImportError(
                "openpyxl es requerido para exportar a Excel. "
                "Instalar con: pip install openpyxl"
            )

        # Estilos
        self.header_font = Font(bold=True, size=11)
        self.header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        self.header_font_white = Font(bold=True, size=11, color="FFFFFF")
        self.center_align = Alignment(horizontal="center", vertical="center")
        self.thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

    def export(self, groove_data: GrooveData, output_path: str) -> str:
        """
        Exporta GrooveData a archivo Excel.

        Args:
            groove_data: Datos del groove a exportar
            output_path: Ruta del archivo de salida (.xlsx)

        Returns:
            Ruta del archivo creado
        """
        wb = openpyxl.Workbook()

        # Eliminar hoja por defecto
        default_sheet = wb.active
        wb.remove(default_sheet)

        # Crear hojas
        self._create_info_sheet(wb, groove_data)
        self._create_rejillas_sheet(wb, groove_data)
        self._create_humanizacion_sheet(wb, groove_data)

        # Guardar
        output_path = Path(output_path)
        if not output_path.suffix:
            output_path = output_path.with_suffix('.xlsx')

        wb.save(str(output_path))
        return str(output_path)

    def _create_info_sheet(self, wb, groove_data: GrooveData):
        """Crea hoja de informacion general."""
        ws = wb.create_sheet("INFO")

        # Encabezado
        ws['A1'] = "GROOVE EXTRACTOR - Analisis"
        ws['A1'].font = Font(bold=True, size=14)
        ws.merge_cells('A1:B1')

        # Datos generales
        info_data = [
            ("Cancion", groove_data.song_name),
            ("BPM", f"{groove_data.bpm:.1f}"),
            ("Estilo", groove_data.style.value),
            ("Vintage", "Si" if groove_data.is_vintage else "No"),
            ("Tempo Drift", f"{groove_data.tempo_drift * 100:.2f}%"),
        ]

        if groove_data.swing:
            info_data.extend([
                ("Swing %", f"{groove_data.swing.swing_percentage:.1f}%"),
                ("Swing Ratio", f"{groove_data.swing.swing_ratio:.2f}"),
                ("Descripcion Swing", groove_data.swing.description),
            ])

        row = 3
        for label, value in info_data:
            ws[f'A{row}'] = label
            ws[f'A{row}'].font = self.header_font
            ws[f'B{row}'] = value
            row += 1

        # Instrumentos
        row += 1
        ws[f'A{row}'] = "Instrumentos Analizados"
        ws[f'A{row}'].font = Font(bold=True, size=12)
        row += 1

        for name, inst in groove_data.instruments.items():
            ws[f'A{row}'] = name
            ws[f'B{row}'] = f"{len(inst.onsets)} onsets, {len(inst.grids)} compases"
            row += 1

        # Ajustar anchos
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 40

    def _create_rejillas_sheet(self, wb, groove_data: GrooveData):
        """
        Crea hoja REJILLAS con patrones de grid.

        Formato:
        ID_PATRON | INSTRUMENTO | 1 | 2 | 3 | ... | 16 | VEL_BASE
        """
        ws = wb.create_sheet("REJILLAS")

        # Encabezados
        headers = ["ID_PATRON", "INSTRUMENTO"] + [str(i) for i in range(1, 17)] + ["VEL_BASE"]

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = self.header_font_white
            cell.fill = self.header_fill
            cell.alignment = self.center_align
            cell.border = self.thin_border

        # Datos
        row = 2
        pattern_id = 1

        for inst_name, inst_data in groove_data.instruments.items():
            for bar_idx, grid in enumerate(inst_data.grids):
                # ID_PATRON
                ws.cell(row=row, column=1, value=f"{inst_name}_{bar_idx + 1}")

                # INSTRUMENTO
                ws.cell(row=row, column=2, value=inst_name)

                # Columnas 1-16 (pattern)
                for step_idx, value in enumerate(grid.pattern):
                    cell = ws.cell(row=row, column=3 + step_idx, value=value)
                    cell.alignment = self.center_align
                    # Colorear celdas con valor 1
                    if value == 1:
                        cell.fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")

                # VEL_BASE (promedio de velocidades no-cero)
                non_zero_vels = [v for v in grid.velocities if v > 0]
                vel_base = int(sum(non_zero_vels) / len(non_zero_vels)) if non_zero_vels else 0
                ws.cell(row=row, column=19, value=vel_base)

                row += 1
                pattern_id += 1

        # Ajustar anchos
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 12
        for col in range(3, 19):
            ws.column_dimensions[get_column_letter(col)].width = 4
        ws.column_dimensions['S'].width = 10

    def _create_humanizacion_sheet(self, wb, groove_data: GrooveData):
        """
        Crea hoja HUMANIZACION con velocidades y timing.

        Formato:
        ID_PATRON | INSTRUMENTO | V1-V16 | T1-T16 | DURATION
        """
        ws = wb.create_sheet("HUMANIZACION")

        # Encabezados
        headers = ["ID_PATRON", "INSTRUMENTO"]
        headers += [f"V{i}" for i in range(1, 17)]  # Velocidades
        headers += [f"T{i}" for i in range(1, 17)]  # Timing deviations
        headers += ["DURATION"]

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = self.header_font_white
            cell.fill = self.header_fill
            cell.alignment = self.center_align
            cell.border = self.thin_border

        # Datos
        row = 2

        for inst_name, inst_data in groove_data.instruments.items():
            for bar_idx, grid in enumerate(inst_data.grids):
                # ID_PATRON
                ws.cell(row=row, column=1, value=f"{inst_name}_{bar_idx + 1}")

                # INSTRUMENTO
                ws.cell(row=row, column=2, value=inst_name)

                # V1-V16 (velocidades)
                for step_idx, vel in enumerate(grid.velocities):
                    cell = ws.cell(row=row, column=3 + step_idx, value=vel)
                    cell.alignment = self.center_align

                # T1-T16 (timing deviations en ms)
                for step_idx, dev in enumerate(grid.timing_deviations):
                    cell = ws.cell(row=row, column=19 + step_idx, value=round(dev, 2))
                    cell.alignment = self.center_align
                    # Colorear basado en desviacion
                    if dev < -5:  # Rushing
                        cell.fill = PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")
                    elif dev > 5:  # Dragging
                        cell.fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")

                # DURATION (duracion del compas en segundos)
                bar_duration = 4 * (60.0 / groove_data.bpm)  # 4 beats
                ws.cell(row=row, column=35, value=round(bar_duration, 3))

                row += 1

        # Ajustar anchos
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 12
        for col in range(3, 35):
            ws.column_dimensions[get_column_letter(col)].width = 5
        ws.column_dimensions[get_column_letter(35)].width = 10

    def export_simple(self, patterns: Dict[str, List[List[int]]],
                      velocities: Dict[str, List[List[int]]],
                      bpm: float,
                      output_path: str) -> str:
        """
        Exportacion simplificada sin GrooveData completo.

        Args:
            patterns: Dict de instrumento -> lista de patrones (cada uno 16 valores 0/1)
            velocities: Dict de instrumento -> lista de velocidades (cada uno 16 valores 0-127)
            bpm: Tempo en BPM
            output_path: Ruta de salida

        Returns:
            Ruta del archivo creado
        """
        # Crear GrooveData minimo
        from ..models import OnsetList, OnsetData

        groove = GrooveData(song_name="export", bpm=bpm)

        for inst_name in patterns:
            inst_patterns = patterns[inst_name]
            inst_velocities = velocities.get(inst_name, [[100]*16] * len(inst_patterns))

            onsets = OnsetList(onsets=[], instrument=inst_name)
            grids = []

            for i, (pattern, vels) in enumerate(zip(inst_patterns, inst_velocities)):
                grid = GridMapping(
                    pattern=pattern,
                    velocities=vels,
                    timing_deviations=[0.0] * 16
                )
                grids.append(grid)

            inst_data = InstrumentData(name=inst_name, onsets=onsets, grids=grids)
            groove.add_instrument(inst_data)

        return self.export(groove, output_path)
