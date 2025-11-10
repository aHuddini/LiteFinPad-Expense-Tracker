"""Centralized configuration constants for visual and behavioral settings."""

# ============================================================================
# WINDOW DIMENSIONS
# ============================================================================

class Window:
    """Main window dimensions."""
    WIDTH = 700
    HEIGHT = 1000
    COMPACT_HEIGHT = 850
    
    MARGIN_RIGHT = 20
    MARGIN_BOTTOM = 20
    MARGIN_LEFT = 20
    MARGIN_TOP = 20
    
class Dialog:
    """Dialog window dimensions and behavior."""
    ADD_EXPENSE_WIDTH = 400
    ADD_EXPENSE_HEIGHT = 670
    ADD_EXPENSE_WITH_NUMPAD_HEIGHT = 750
    
    EDIT_EXPENSE_WIDTH = 350
    EDIT_EXPENSE_HEIGHT = 410
    
    ABOUT_WIDTH = 450
    ABOUT_HEIGHT = 600
    
    BUDGET_WIDTH = 400
    BUDGET_HEIGHT = 670
    
    EXPORT_WIDTH = 500
    EXPORT_HEIGHT = 535
    EXPORT_GAP = 10
    
    FOCUS_LOSS_DELAY_MS = 100
    AUTO_CLOSE_ENABLED = True
    
    DEFAULT_OFFSET_X = 20
    DEFAULT_OFFSET_Y = 20

# ============================================================================
# COLORS
# ============================================================================

class Colors:
    """Color palette for the application."""
    
    BG_WHITE = '#ffffff'
    BG_LIGHT_GRAY = '#e5e5e5'
    BG_MEDIUM_GRAY = '#e0e0e0'
    BG_DARK_GRAY = '#d0d0d0'
    BG_BUTTON_DISABLED = '#D0D0D0'
    BG_DIALOG = '#f8f9fa'
    BG_TOTAL_ROW = '#E7E6E6'
    BG_ARCHIVE_TINT = '#E0DDF0'
    
    DATE_BG = '#2E5C8A'
    DATE_FG = 'white'
    
    TEXT_BLACK = '#1a1a1a'
    TEXT_GRAY_DARK = '#323130'
    TEXT_GRAY_MEDIUM = '#605e5c'
    TEXT_GRAY_LIGHT = '#888888'
    TEXT_BROWN = '#8B4513'
    
    GREEN_PRIMARY = '#107c10'
    GREEN_HOVER = '#0e6b0e'
    GREEN_PRESSED = '#0c5a0c'
    
    BLUE_PRIMARY = '#0078D4'
    BLUE_LINK = '#0078D4'
    BLUE_NAVY = '#4A8FCE'
    BLUE_NAVY_DARK = '#3A7FBE'
    BLUE_DARK_NAVY = '#1E3A8A'
    BLUE_SELECTED = '#0078d4'
    
    RED_PRIMARY = '#8B0000'
    RED_INCREASE = '#C00000'
    
    ORANGE_PRIMARY = '#E67E00'
    ORANGE_DARK = '#CC6600'
    
    # Archive/Purple
    PURPLE_ARCHIVE = '#4A4A8A'  # Archive mode accent color
    
    # Trend/Purple
    PURPLE_PRIMARY = '#4A4A8A'  # Previous month, trend analysis (original)
    PURPLE_VIBRANT = '#6B2599'  # Previous month label (vibrant purple, slightly darker)
    
    # Averages (non-primary colors)
    TEAL_DARK = '#008B8B'  # Daily Average label (dark cyan/teal)
    AMBER_DARK = '#B8860B'  # Weekly Average label (dark goldenrod)
    
    # === Button States ===
    BUTTON_ACTIVE_BG = '#e0e0e0'
    BUTTON_PRESSED_BG = '#d0d0d0'


class DarkModeColors:
    """Dark mode color palette."""
    
    BG_WHITE = '#1e1e1e'
    BG_MAIN = '#1e1e1e'
    BG_SECONDARY = '#252526'
    BG_TERTIARY = '#2d2d30'
    BG_LIGHT_GRAY = '#2d2d30'
    BG_MEDIUM_GRAY = '#3f3f46'
    BG_DARK_GRAY = '#3f3f46'
    BG_BUTTON_DISABLED = '#3f3f46'
    BG_DIALOG = '#2d2d30'
    BG_TOTAL_ROW = '#3f3f46'
    BG_ARCHIVE_TINT = '#3d2d4d'
    BG_TABLE = '#2a2d3a'
    
    DATE_BG = '#2E5C8A'
    DATE_FG = 'white'
    
    TEXT_PRIMARY = '#cccccc'
    TEXT_BLACK = '#cccccc'
    TEXT_SECONDARY = '#a0a0a0'
    TEXT_GRAY_DARK = '#a0a0a0'
    TEXT_TERTIARY = '#808080'
    TEXT_GRAY_MEDIUM = '#808080'
    TEXT_GRAY_LIGHT = '#666666'
    TEXT_BROWN = '#d4a574'
    
    GREEN_PRIMARY = '#00cc66'
    GREEN_BUTTON = '#107c10'
    GREEN_HOVER = '#00b359'
    GREEN_PRESSED = '#00994d'
    
    BLUE_PRIMARY = '#4fc3f7'
    BLUE_LINK = '#4fc3f7'
    BLUE_NAVY = '#5eb3f5'
    BLUE_NAVY_DARK = '#4da3e5'
    BLUE_DARK_NAVY = '#1E3A8A'
    BLUE_BUDGET = '#3E6AAA'
    BLUE_SELECTED = '#4fc3f7'
    
    RED_PRIMARY = '#f48771'
    RED_INCREASE = '#ff6b5a'
    
    ORANGE_PRIMARY = '#ffa726'
    ORANGE_DARK = '#ff9800'
    
    PURPLE_ARCHIVE = '#9c7bb8'
    
    PURPLE_PRIMARY = '#9c7bb8'
    PURPLE_VIBRANT = '#ba68c8'
    
    TEAL_DARK = '#4dd0e1'
    AMBER_DARK = '#ffb74d'
    
    BUTTON_ACTIVE_BG = '#3f3f46'
    BUTTON_PRESSED_BG = '#2d2d30'

# ============================================================================
# FONTS
# ============================================================================

class Fonts:
    """Font configuration."""
    
    FAMILY = 'Segoe UI'
    
    SIZE_TINY = 9
    SIZE_SMALL = 10
    SIZE_NORMAL = 11
    SIZE_MEDIUM = 12
    SIZE_LARGE = 13
    SIZE_XLARGE = 14
    SIZE_TITLE = 18
    SIZE_HERO = 20
    SIZE_HUGE = 22
    SIZE_MASSIVE = 38
    
    TITLE = (FAMILY, SIZE_HUGE, 'bold')
    SUBTITLE = (FAMILY, SIZE_TITLE, 'bold')
    HERO_TOTAL = (FAMILY, SIZE_MASSIVE, 'bold')
    HEADER = (FAMILY, SIZE_XLARGE, 'bold')
    BUTTON = (FAMILY, SIZE_MEDIUM, 'bold')
    LABEL = (FAMILY, SIZE_SMALL)
    LABEL_SMALL = (FAMILY, SIZE_TINY)
    ENTRY = (FAMILY, SIZE_NORMAL)
    TOOLTIP = (FAMILY, SIZE_TINY)
    LINK = (FAMILY, SIZE_TINY, 'underline')
    ABOUT_TITLE = (FAMILY, SIZE_HERO, 'bold')

# ============================================================================
# ANIMATION
# ============================================================================

class Animation:
    """Window animation parameters."""
    
    SLIDE_OUT_DURATION_MS = 220
    EASE_OUT_POWER = 1.4
    FADE_START_PROGRESS = 0.6
    FADE_END_OPACITY = 0.3
    
    FADE_IN_STEPS = [0.2, 0.4, 0.6, 0.8, 1.0]
    FADE_IN_STEP_DELAY_MS = 10
    FADE_IN_INITIAL_DELAY_MS = 1
    
    SCREEN_MARGIN = 20

# ============================================================================
# UI COMPONENTS
# ============================================================================

class NumberPad:
    """Number pad widget configuration."""
    
    BUTTON_WIDTH = 2
    FONT_SIZE = 12
    FONT_WEIGHT = 'bold'
    PADDING = (8, 10)
    GRID_SPACING = 5
    FRAME_PADDING = 10
    MAX_AMOUNT_LENGTH = 10

class TreeView:
    """Treeview/Table configuration."""
    
    ROW_HEIGHT = 28
    
    HEADER_FONT_SIZE = 10
    BODY_FONT_SIZE = 10
    
    COL_DATE_WIDTH = 120
    COL_DESCRIPTION_WIDTH = 350
    COL_AMOUNT_WIDTH = 120
    
    SCROLL_SPEED = 3
    SELECTION_BG = '#0078d4'
    SELECTION_FG = 'white'
    ALTERNATING_ROWS = False
    ALT_ROW_COLOR = '#f5f5f5'
    
    SORT_ASCENDING_ICON = '↑'
    SORT_DESCENDING_ICON = '↓'
    DEFAULT_SORT_COLUMN = 'Date'
    DEFAULT_SORT_ORDER = 'desc'

class Export:
    """Export dialog and file configuration."""
    
    DIALOG_WIDTH = 400
    DIALOG_HEIGHT = 300
    
    # Excel export colors
    EXCEL_HEADER_BG = '#0078D4'
    EXCEL_HEADER_FG = 'white'
    EXCEL_TOTAL_BG = '#E7E6E6'

# ============================================================================
# VALIDATION
# ============================================================================

class Validation:
    """Input validation parameters."""
    
    MAX_AMOUNT_VALUE = 9999999.99
    MAX_AMOUNT_DECIMALS = 2
    MAX_DESCRIPTION_LENGTH = 200
    MIN_DESCRIPTION_LENGTH = 1

# ============================================================================
# APPLICATION INFO
# ============================================================================

class App:
    """Application metadata."""
    
    NAME = "LiteFinPad"
    TAGLINE = "Monthly Expense Tracker"
    DESCRIPTION = "A simple, offline expense tracker for Windows."
    LICENSE = "MIT License"
    BUILT_WITH = "Built with AI assistance (Cursor + Claude Sonnet 4)"
    GITHUB_URL = "https://github.com/aHuddini/LiteFinPad"
    OFFLINE_NOTICE = "100% offline - no internet connection required"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_font(size, weight=None):
    """Get font tuple with standard family."""
    if weight:
        return (Fonts.FAMILY, size, weight)
    return (Fonts.FAMILY, size)

class StatusBar:
    """Status bar configuration for minimal feedback."""
    HEIGHT = 25
    BG_COLOR = '#e5e5e5'  # Slightly darker gray to match ttk widget backgrounds
    TEXT_COLOR = '#323130'  # Match main text color (Colors.TEXT_GRAY_DARK)
    BORDER_COLOR = '#d0d0d0'  # Match border/separator color
    
    # Status icons
    SUCCESS_ICON = '✅'
    ERROR_ICON = '⚠️'
    INFO_ICON = 'ℹ️'
    
    # Auto-clear behavior
    CLEAR_DELAY_MS = 5000  # Clear after 5 seconds

# ============================================================================
# THREADING & TIMING
# ============================================================================

class Threading:
    """Threading and timing parameters."""
    FOCUS_CHECK_DELAY_MS = 100  # Delay before checking focus change
    GUI_QUEUE_POLL_MS = 20      # GUI queue processing interval

# ============================================================================
# USER MESSAGES
# ============================================================================

class Messages:
    """User-facing error and info messages."""
    
    # Dialog titles
    TITLE_ERROR = "Error"
    TITLE_WARNING = "Warning"
    TITLE_SUCCESS = "Success"
    TITLE_VALIDATION = "Validation Error"
    TITLE_IMPORT = "Import Backup"
    TITLE_EXPORT = "Export Expenses"
    TITLE_NO_SELECTION = "No Selection"
    TITLE_DELETE_CONFIRM = "Confirm Delete"
    TITLE_IMPORT_SUCCESS = "Import Successful"
    TITLE_IMPORT_ERROR = "Import Error"
    TITLE_EXPORT_SUCCESS = "Export Successful"
    TITLE_EXPORT_ERROR = "Export Error"
    
    # Validation errors
    AMOUNT_REQUIRED = "Please enter an amount"
    AMOUNT_INVALID = "Please enter a valid number"
    AMOUNT_POSITIVE = "Amount must be greater than 0"
    DESCRIPTION_REQUIRED = "Please enter a description"
    DATE_REQUIRED = "Please select a valid date"
    
    # Selection warnings
    NO_SELECTION_EDIT = "Please select an expense to edit."
    NO_SELECTION_DELETE = "Please select an expense to delete."
    
    # Delete confirmation
    DELETE_CONFIRM = "Are you sure you want to delete this expense?\n\n{description}\n{amount}\n{date}"
    
    # Status bar success messages
    EXPENSE_ADDED = "Expense added"
    EXPENSE_EDITED = "Expense edited successfully"
    EXPENSE_DELETED = "Expense deleted"
    
    # Import messages
    IMPORT_NO_FILE = "No file selected"
    IMPORT_INVALID_FORMAT = "Invalid backup file format"
    IMPORT_INVALID_JSON = "Invalid JSON file"
    IMPORT_INVALID_STRUCTURE = "Backup file has invalid structure"
    IMPORT_SUCCESS = "Imported {count} expenses successfully from {month}"
    IMPORT_FAILED = "Failed to import backup file"
    IMPORT_NO_EXPENSES = "No expenses found in backup file"
    
    # Export messages
    EXPORT_SUCCESS_EXCEL = "Exported to Excel: {filename}"
    EXPORT_SUCCESS_PDF = "Exported to PDF: {filename}"
    EXPORT_SUCCESS_JSON = "Backup created: {filename}"
    EXPORT_FAILED = "Failed to export expenses"
    EXPORT_NO_EXPENSES = "No expenses to export for {month} {year}"
    
    # Export/Display labels (reused in multiple export formats)
    LABEL_TOTAL_EXPENSES = "Total Expenses:"
    LABEL_TOTAL_AMOUNT = "Total Amount:"
    
    # Data operation errors
    ERROR_LOADING_DATA = "Error loading data"
    ERROR_SAVING_DATA = "Error saving data"
    
    # Status bar messages
    STATUS_EXPENSE_ADDED = "Expense added successfully"
    STATUS_EXPENSE_UPDATED = "Expense updated successfully"
    STATUS_EXPENSE_DELETED = "Expense deleted successfully"
    STATUS_DATA_LOADED = "Data loaded successfully"
    STATUS_EXPORT_COMPLETE = "Export complete"
    STATUS_IMPORT_COMPLETE = "Import complete"

# ============================================================================
# CUSTOMTKINTER THEME CONFIGURATION
# ============================================================================

class CustomTkinterTheme:
    """CustomTkinter theme and appearance settings."""
    
    # === Appearance Mode ===
    # Options: "light", "dark", "system" (follows system theme)
    APPEARANCE_MODE = "light"  # Light mode to match existing light gray backgrounds
    
    # === Color Theme ===
    # Options: "blue", "green", "dark-blue"
    COLOR_THEME = "blue"  # Default color scheme
    
    # === Widget Appearance ===
    CORNER_RADIUS = 8  # Rounded corners for buttons, entries, etc.
    BORDER_WIDTH = 1  # Border width for widgets
    
    # === Widget Dimensions ===
    BUTTON_HEIGHT = 35  # Standard button height
    ENTRY_HEIGHT = 35  # Standard entry field height
    
    # === Widget Spacing ===
    BUTTON_PADY = 5  # Vertical padding for buttons
    ENTRY_PADY = 5  # Vertical padding for entries
    
    # === Note ===
    # CustomTkinter is a visual styling library only.
    # It does NOT fix functional limitations (like auto-complete dropdown issues).
    # CTkComboBox has the same limitations as ttk.Combobox.

# ============================================================================
# FILE PATTERNS
# ============================================================================

class Files:
    """File naming patterns and extensions."""
    
    # Data files
    EXPENSES_FILENAME = "expenses.json"
    CALCULATIONS_FILENAME = "calculations.json"
    
    # Backup/Export prefixes
    BACKUP_PREFIX = "LiteFinPad_Backup"
    EXPORT_EXCEL_PREFIX = "LF"
    EXPORT_PDF_PREFIX = "LF"
    
    # File extensions
    JSON_EXT = ".json"
    EXCEL_EXT = ".xlsx"
    PDF_EXT = ".pdf"
    CSV_EXT = ".csv"
    
    # Folder patterns
    DATA_FOLDER_PREFIX = "data_"  # data_2025-10
    
    @staticmethod
    def get_data_folder(year_month):
        """Generate data folder name."""
        return f"{Files.DATA_FOLDER_PREFIX}{year_month}"
    
    @staticmethod
    def get_backup_filename(timestamp):
        """Generate backup filename."""
        return f"{Files.BACKUP_PREFIX}_{timestamp}{Files.JSON_EXT}"
    
    @staticmethod
    def get_export_filename(month, year, format_type):
        """Generate export filename based on format."""
        if format_type == "excel":
            return f"{Files.EXPORT_EXCEL_PREFIX}_{month}_{year}_Expenses{Files.EXCEL_EXT}"
        elif format_type == "pdf":
            return f"{Files.EXPORT_PDF_PREFIX}_{month}_{year}_Expenses{Files.PDF_EXT}"
        return None


def get_window_geometry(width, height, x, y):
    """Format geometry string for Tkinter (WIDTHxHEIGHT+X+Y)."""
    return f"{width}x{height}+{x}+{y}"

