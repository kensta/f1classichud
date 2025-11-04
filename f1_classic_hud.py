######################################################################
# F1 CLASSIC HUD by Kenji Kumakura <kenji.kumakura@gmail.com>
#
# Version 1.1.0
######################################################################
# 1.1.0
# - Refactored code to reduce duplication
# - Extracted constants for better maintainability
# - Added helper method for label creation
# - Eliminated global variables
# - Unified bar drawing functions
# - Improved error handling and logging
# - Added comprehensive documentation
# - Optimized repeated calculations
# - Added input validation
#
# 1.0.1
# - Added inner shadow to RPM and GAS bars
# - Replaced the remaining texts from background image to native text
#   -> The only image kept is the green circle around gear numbers
######################################################################
import ac
import acsys
import os
import sys
import platform

if platform.architecture()[0] == "64bit":
    libdir = 'third_party/lib64'
else:
    libdir = 'third_party/lib'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), libdir))
os.environ['PATH'] = os.environ['PATH'] + ";."

from third_party.sim_info import info
from third_party.util import *

# =============================================================================
# CONSTANTS
# =============================================================================

# Window dimensions
APP_WIDTH = 940
APP_HEIGHT = 280
SCALE = 1
APP_PATH = "apps/python/f1_classic_hud/"

# Colors (RGBA)
COLOR_TEXT = (0.89, 0.89, 0.89, 1)
COLOR_SHADOW = (0.2, 0.2, 0.2, 1)
COLOR_LABEL_ACCENT = (0.7, 0.77, 0, 1)  # Yellow-green for RPM/GAS/Km/h labels
COLOR_RPM_BAR = (0, 0.6, 0.9, 1)  # Cyan
COLOR_GAS_BAR = (0, 0.8, 0.1, 1)  # Green
COLOR_BORDER = (0.89, 0.89, 0.89, 1)

# Shadow settings
SHADOW_OFFSET = (2, 2)  # x, y offset for text shadows

# Font settings
FONT_NAME = "MonospaceTypewriter"
FONT_SIZE_XLARGE = 55
FONT_SIZE_LARGE = 45
FONT_SIZE_MEDIUM = 30

# Bar dimensions
BAR_WIDTH_MAX = 414
BAR_HEIGHT = 50
BAR_RPM_X = 147
BAR_RPM_Y = 113
BAR_GAS_X = 147
BAR_GAS_Y = 189

# Border positions for RPM bar
BORDER_RPM_TOP_Y = 108
BORDER_RPM_BOTTOM_Y = 163
BORDER_RPM_LEFT_X = 142
BORDER_RPM_RIGHT_X = 560

# Border positions for GAS bar
BORDER_GAS_TOP_Y = 184
BORDER_GAS_BOTTOM_Y = 239
BORDER_GAS_LEFT_X = 142
BORDER_GAS_RIGHT_X = 560

# Label positions (name, x, y, font_size, alignment, color)
# Format: (x, y, font_size, alignment, color)
LABEL_POSITIONS = {
    'pilot': (1, 0, FONT_SIZE_LARGE, "left", COLOR_TEXT),
    'gear': (654, 137, FONT_SIZE_XLARGE, "left", COLOR_TEXT),
    'speed': (849, 165, FONT_SIZE_XLARGE, "center", COLOR_TEXT),
    'rpm_max': (566, 65, FONT_SIZE_MEDIUM, "right", COLOR_TEXT),
    'rpm_zero': (160, 65, FONT_SIZE_MEDIUM, "right", COLOR_TEXT),
    'rpm_label': (1, 106, FONT_SIZE_LARGE, "left", COLOR_LABEL_ACCENT),
    'gas_hundred': (567, 240, FONT_SIZE_MEDIUM, "right", COLOR_TEXT),
    'gas_percent': (362, 240, FONT_SIZE_MEDIUM, "right", COLOR_TEXT),
    'gas_zero': (160, 240, FONT_SIZE_MEDIUM, "right", COLOR_TEXT),
    'gas_label': (1, 184, FONT_SIZE_LARGE, "left", COLOR_LABEL_ACCENT),
    'kmh': (792, 108, FONT_SIZE_LARGE, "left", COLOR_LABEL_ACCENT),
}

# Gear circle texture
GEAR_CIRCLE_POS = (598, 99)
GEAR_CIRCLE_SIZE = (150, 150)

# =============================================================================
# MAIN HUD CLASS
# =============================================================================

class AppHud:
    """
    HUD clássico de F1 para Assetto Corsa.

    Exibe telemetria em tempo real do veículo:
    - RPM com barra de progresso visual
    - Marcha atual (R, N, 1-8)
    - Velocidade em km/h
    - Acelerador (GAS) com barra de progresso
    - Nome do piloto

    Attributes:
        window: Janela principal do aplicativo
        rpm_bar_value: Valor atual da barra de RPM (0-100%)
        gas_bar_value: Valor atual da barra de acelerador (0-100%)
        rpm_max: RPM máximo do veículo
        rpm_percent_part: Fator de conversão para cálculo de porcentagem
    """

    def __init__(self, window):
        """
        Inicializa o HUD com todos os elementos visuais.

        Args:
            window: Referência para a janela do aplicativo AC
        """
        self.window = window

        # Initialize bar values (instance variables instead of globals)
        self.rpm_bar_value = 0
        self.gas_bar_value = 20

        # Initialize car values and pre-calculate constants
        if info.static.maxRpm and info.static.maxRpm > 0:
            self.rpm_max = info.static.maxRpm
            self.rpm_percent_part = info.static.maxRpm / 100.0
        else:
            self.rpm_max = 0
            self.rpm_percent_part = 1.0
            ac.log("f1_classic_hud: Warning - maxRpm not available or invalid")

        # Configure window
        ac.setTitle(self.window, "")
        ac.drawBorder(self.window, 0)
        ac.setIconPosition(self.window, 0, -10000)
        ac.setSize(self.window, round(APP_WIDTH * SCALE), round(APP_HEIGHT * SCALE))

        ac.addRenderCallback(self.window, onFormRender)

        # Create gear circle texture
        self.gear_circle = ac.addLabel(self.window, "")
        ac.setSize(self.gear_circle, *GEAR_CIRCLE_SIZE)
        ac.setPosition(self.gear_circle, *GEAR_CIRCLE_POS)
        ac.setBackgroundTexture(self.gear_circle, APP_PATH + "textures/gear_circle.png")

        # Initialize all labels using helper method
        self._create_all_labels()

    def _create_label_with_shadow(self, text, x, y, font_size,
                                   alignment="left", color=COLOR_TEXT):
        """
        Cria um label com sombra automaticamente.

        Este método helper reduz duplicação de código ao criar pares de labels
        (principal + sombra) com configurações consistentes.

        Args:
            text: Texto inicial do label
            x: Posição X do label principal
            y: Posição Y do label principal
            font_size: Tamanho da fonte
            alignment: Alinhamento do texto ("left", "center", "right")
            color: Cor do texto principal (RGBA tuple)

        Returns:
            tuple: (label_principal, label_shadow)
        """
        # Create shadow label (offset position)
        shadow = ac.addLabel(self.window, text)
        ac.setPosition(shadow, x + SHADOW_OFFSET[0], y + SHADOW_OFFSET[1])
        ac.setFontSize(shadow, font_size)
        ac.setCustomFont(shadow, FONT_NAME, 0, 1)
        ac.setFontColor(shadow, *COLOR_SHADOW)
        ac.setFontAlignment(shadow, alignment)

        # Create main label
        label = ac.addLabel(self.window, text)
        ac.setPosition(label, x, y)
        ac.setFontSize(label, font_size)
        ac.setCustomFont(label, FONT_NAME, 0, 1)
        ac.setFontColor(label, *color)
        ac.setFontAlignment(label, alignment)

        return label, shadow

    def _create_all_labels(self):
        """
        Cria todos os labels do HUD usando o método helper.

        Organiza a criação de todos os elementos de texto do HUD,
        incluindo valores dinâmicos e estáticos.
        """
        # Pilot name
        x, y, size, align, color = LABEL_POSITIONS['pilot']
        self.pilot_label, self.pilot_label_shadow = self._create_label_with_shadow(
            info.static.playerName, x, y, size, align, color
        )

        # Gear display
        x, y, size, align, color = LABEL_POSITIONS['gear']
        self.gear_label, self.gear_label_shadow = self._create_label_with_shadow(
            "", x, y, size, align, color
        )

        # Speed display
        x, y, size, align, color = LABEL_POSITIONS['speed']
        self.speed_label, self.speed_label_shadow = self._create_label_with_shadow(
            "", x, y, size, align, color
        )

        # RPM max label
        x, y, size, align, color = LABEL_POSITIONS['rpm_max']
        self.rpm_max_label, self.rpm_max_shadow = self._create_label_with_shadow(
            str(self.rpm_max), x, y, size, align, color
        )

        # RPM zero label
        x, y, size, align, color = LABEL_POSITIONS['rpm_zero']
        self.rpm_zero_label, self.rpm_zero_shadow = self._create_label_with_shadow(
            "0", x, y, size, align, color
        )

        # GAS hundred label
        x, y, size, align, color = LABEL_POSITIONS['gas_hundred']
        self.gas_hundred_label, self.gas_hundred_shadow = self._create_label_with_shadow(
            "100", x, y, size, align, color
        )

        # GAS percent symbol
        x, y, size, align, color = LABEL_POSITIONS['gas_percent']
        self.gas_percent_label, self.gas_percent_shadow = self._create_label_with_shadow(
            "%", x, y, size, align, color
        )

        # GAS zero label
        x, y, size, align, color = LABEL_POSITIONS['gas_zero']
        self.gas_zero_label, self.gas_zero_shadow = self._create_label_with_shadow(
            "0", x, y, size, align, color
        )

        # RPM text label
        x, y, size, align, color = LABEL_POSITIONS['rpm_label']
        self.rpm_text_label, self.rpm_text_shadow = self._create_label_with_shadow(
            "RPM", x, y, size, align, color
        )

        # GAS text label
        x, y, size, align, color = LABEL_POSITIONS['gas_label']
        self.gas_text_label, self.gas_text_shadow = self._create_label_with_shadow(
            "GAS", x, y, size, align, color
        )

        # Km/h text label
        x, y, size, align, color = LABEL_POSITIONS['kmh']
        self.kmh_label, self.kmh_shadow = self._create_label_with_shadow(
            "Km/h", x, y, size, align, color
        )

    def update_gears(self):
        """
        Atualiza o display de marcha atual.

        Converte valores numéricos do simulador para representação visual:
        - 0 = R (Ré)
        - 1 = N (Neutro)
        - 2+ = Marchas 1-8
        """
        try:
            current_gear = ac.getCarState(0, acsys.CS.Gear)

            # Validate gear value
            if not isinstance(current_gear, (int, float)):
                ac.log(f"f1_classic_hud: Invalid gear value type: {type(current_gear)}")
                current_gear = 1  # Default to Neutral

            # Convert gear number to display string
            if current_gear == 0:
                current_gear_s = "R"
            elif current_gear == 1:
                current_gear_s = "N"
            else:
                current_gear_s = str(int(current_gear - 1))

            ac.setText(self.gear_label, current_gear_s)
            ac.setText(self.gear_label_shadow, current_gear_s)

        except Exception as e:
            ac.log(f"f1_classic_hud: Error updating gears: {e}")

    def update_speed(self):
        """
        Atualiza o display de velocidade em km/h.

        Lê a velocidade atual do veículo e atualiza os labels
        com validação de valores.
        """
        try:
            current_speed = ac.getCarState(0, acsys.CS.SpeedKMH)

            # Validate and clamp speed value
            if not isinstance(current_speed, (int, float)):
                current_speed = 0
            current_speed = max(0, round(current_speed))

            speed_text = str(current_speed)
            ac.setText(self.speed_label, speed_text)
            ac.setText(self.speed_label_shadow, speed_text)

        except Exception as e:
            ac.log(f"f1_classic_hud: Error updating speed: {e}")

    def update_pedals(self):
        """
        Atualiza o valor do acelerador (GAS).

        Lê a entrada do pedal de acelerador e converte para porcentagem (0-100).
        """
        try:
            throttle_value = ac.getCarState(0, acsys.CS.Gas)

            # Validate and clamp throttle value
            if not isinstance(throttle_value, (int, float)):
                throttle_value = 0

            throttle_value = max(0.0, min(1.0, throttle_value))  # Clamp to 0-1
            self.gas_bar_value = round(throttle_value * 100)

        except Exception as e:
            ac.log(f"f1_classic_hud: Error updating pedals: {e}")
            self.gas_bar_value = 0

    def update_rpm(self):
        """
        Atualiza o valor de RPM e calcula a porcentagem para a barra.

        Converte RPM atual para porcentagem baseado no RPM máximo do veículo.
        """
        try:
            current_rpm = ac.getCarState(0, acsys.CS.RPM)

            # Validate RPM value
            if not isinstance(current_rpm, (int, float)):
                current_rpm = 0

            current_rpm = max(0, round(current_rpm))

            # Calculate percentage using pre-calculated factor
            if self.rpm_percent_part > 0:
                percent_calc = current_rpm / self.rpm_percent_part
                self.rpm_bar_value = max(0, min(100, percent_calc))  # Clamp 0-100
            else:
                self.rpm_bar_value = 0

        except Exception as e:
            ac.log(f"f1_classic_hud: Error updating RPM: {e}")
            self.rpm_bar_value = 0

    def on_update(self, deltaT):
        """
        Função de update principal chamada a cada frame.

        Args:
            deltaT: Delta time desde o último frame
        """
        try:
            ac.setBackgroundOpacity(self.window, 0)
            self.update_pedals()
            self.update_rpm()
            self.update_gears()
            self.update_speed()
        except Exception as e:
            ac.log(f"f1_classic_hud: Error in on_update: {e}")

    def on_shutdown(self):
        """
        Função de limpeza chamada ao desligar o aplicativo.
        """
        try:
            self.rpm_max = 0
            ac.log("f1_classic_hud: Shutdown complete")
        except Exception as e:
            ac.log(f"f1_classic_hud: Error during shutdown: {e}")

# =============================================================================
# RENDERING FUNCTIONS
# =============================================================================

def drawBar(value, x, y, width_max, height, color):
    """
    Desenha uma barra de progresso horizontal genérica.

    Args:
        value: Valor da barra (0-100%)
        x: Posição X inicial
        y: Posição Y inicial
        width_max: Largura máxima da barra em pixels
        height: Altura da barra em pixels
        color: Cor da barra (RGBA tuple)
    """
    # Validate input
    value = max(0, min(100, value))

    # Calculate bar width based on percentage
    bar_percent_part = width_max / 100.0
    bar_percent_value = value * bar_percent_part

    ac.glColor4f(*color)
    ac.glQuad(x, y, bar_percent_value, height)

def drawRpmBar(value):
    """
    Desenha a barra de RPM.

    Args:
        value: Valor de RPM em porcentagem (0-100)
    """
    drawBar(value, BAR_RPM_X, BAR_RPM_Y, BAR_WIDTH_MAX, BAR_HEIGHT, COLOR_RPM_BAR)

def drawGasBar(value):
    """
    Desenha a barra de acelerador (GAS).

    Args:
        value: Valor do acelerador em porcentagem (0-100)
    """
    drawBar(value, BAR_GAS_X, BAR_GAS_Y, BAR_WIDTH_MAX, BAR_HEIGHT, COLOR_GAS_BAR)

def drawBarBorder(top_y, bottom_y, left_x, right_x, inner_y):
    """
    Desenha borda e sombras internas para uma barra de progresso.

    Cria efeito 3D com múltiplas camadas de sombra.

    Args:
        top_y: Posição Y do topo da borda
        bottom_y: Posição Y do fundo da borda
        left_x: Posição X da borda esquerda
        right_x: Posição X da borda direita
        inner_y: Posição Y do início da área interna
    """
    # Border shadow layer 1
    ac.glColor4f(0, 0, 0, 0.4)
    ac.glQuad(left_x + 2, top_y - 2, 424, 5)  # top
    ac.glQuad(right_x + 3, top_y + 2, 5, 55)  # right
    ac.glQuad(left_x + 2, bottom_y - 2, 424, 5)  # bottom

    # Border shadow layer 2
    ac.glColor4f(0, 0, 0, 0.2)
    ac.glQuad(left_x + 2, top_y - 3, 424, 5)  # top
    ac.glQuad(right_x + 3, top_y - 2, 5, 55)  # right
    ac.glQuad(left_x + 2, bottom_y - 2, 424, 5)  # bottom

    # Horizontal top inner shadow
    ac.glColor4f(0, 0, 0, 0.4)
    ac.glQuad(BAR_RPM_X, inner_y, BAR_WIDTH_MAX, 1)
    ac.glColor4f(0, 0, 0, 0.2)
    ac.glQuad(BAR_RPM_X, inner_y + 1, BAR_WIDTH_MAX, 1)
    ac.glColor4f(0, 0, 0, 0.1)
    ac.glQuad(BAR_RPM_X, inner_y + 2, BAR_WIDTH_MAX, 1)

    # Horizontal bottom inner shadow
    bottom_inner_y = inner_y + BAR_HEIGHT - 1
    ac.glColor4f(0, 0, 0, 0.8)
    ac.glQuad(BAR_RPM_X, bottom_inner_y, BAR_WIDTH_MAX, 1)
    ac.glColor4f(0, 0, 0, 0.6)
    ac.glQuad(BAR_RPM_X, bottom_inner_y - 1, BAR_WIDTH_MAX, 1)
    ac.glColor4f(0, 0, 0, 0.4)
    ac.glQuad(BAR_RPM_X, bottom_inner_y - 2, BAR_WIDTH_MAX, 1)
    ac.glColor4f(0, 0, 0, 0.2)
    ac.glQuad(BAR_RPM_X, bottom_inner_y - 3, BAR_WIDTH_MAX, 1)
    ac.glColor4f(0, 0, 0, 0.1)
    ac.glQuad(BAR_RPM_X, bottom_inner_y - 4, BAR_WIDTH_MAX, 1)

    # Vertical inner shadows (left side)
    for i, alpha in enumerate([0.8, 0.6, 0.4, 0.2, 0.1]):
        ac.glColor4f(0, 0, 0, alpha)
        ac.glQuad(BAR_RPM_X + i, inner_y, 1, BAR_HEIGHT)

    # Border
    ac.glColor4f(*COLOR_BORDER)
    ac.glQuad(left_x, top_y, 5, 55)  # left
    ac.glQuad(left_x, top_y, 423, 5)  # top
    ac.glQuad(right_x, top_y, 5, 55)  # right
    ac.glQuad(left_x, bottom_y, 423, 5)  # bottom

def drawRpmBarBorder():
    """Desenha a borda e sombras da barra de RPM."""
    drawBarBorder(BORDER_RPM_TOP_Y, BORDER_RPM_BOTTOM_Y,
                  BORDER_RPM_LEFT_X, BORDER_RPM_RIGHT_X, BAR_RPM_Y)

def drawGasBarBorder():
    """Desenha a borda e sombras da barra de GAS."""
    drawBarBorder(BORDER_GAS_TOP_Y, BORDER_GAS_BOTTOM_Y,
                  BORDER_GAS_LEFT_X, BORDER_GAS_RIGHT_X, BAR_GAS_Y)

def onFormRender(deltaT):
    """
    Callback de renderização chamado a cada frame.

    Desenha todas as barras e bordas na ordem correta.

    Args:
        deltaT: Delta time desde o último frame
    """
    try:
        # Draw bars first (background)
        drawRpmBar(app_hud.rpm_bar_value)
        drawGasBar(app_hud.gas_bar_value)

        # Draw borders on top
        drawRpmBarBorder()
        drawGasBarBorder()
    except Exception as e:
        ac.log(f"f1_classic_hud: Error in onFormRender: {e}")

# =============================================================================
# LIFECYCLE FUNCTIONS
# =============================================================================

def acMain(ac_version):
    """
    Função principal de inicialização do aplicativo.

    Chamada uma vez quando o Assetto Corsa carrega o plugin.

    Args:
        ac_version: Versão do Assetto Corsa
    """
    global app_window, app_hud
    try:
        app_window = ac.newApp("F1 Classic HUD")
        app_hud = AppHud(app_window)
        ac.log("f1_classic_hud: Initialized successfully (v1.1.0)")
        ac.console("F1 Classic HUD v1.1.0 loaded")
    except FileNotFoundError as e:
        ac.log(f"f1_classic_hud: Texture file not found: {e}")
        ac.console(f"F1 HUD ERROR: Missing texture files - {e}")
    except Exception as e:
        ac.console(f"f1_classic_hud: acMain() failure: {e}")
        ac.log(f"f1_classic_hud: acMain() failure: {e}")
        import traceback
        ac.log(traceback.format_exc())

def acUpdate(deltaT):
    """
    Função de update chamada a cada frame.

    Args:
        deltaT: Delta time desde o último frame
    """
    try:
        app_hud.on_update(deltaT)
    except Exception as e:
        ac.console(f"f1_classic_hud: acUpdate() failure: {e}")
        ac.log(f"f1_classic_hud: acUpdate() failure: {e}")

def acShutdown():
    """
    Função de limpeza chamada quando o aplicativo é desligado.
    """
    try:
        app_hud.on_shutdown()
    except Exception as e:
        ac.log(f"f1_classic_hud: acShutdown() failure: {e}")
