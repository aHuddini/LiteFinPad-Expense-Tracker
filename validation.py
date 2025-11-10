"""Input validation functions for expense tracker. All functions are pure (no side effects)."""

from typing import Any, Optional


class ValidationResult:
    """
    Structured validation result object.
    
    Contains validation status, error message, sanitized value, and field name.
    Works in boolean context (if result:).
    """
    
    def __init__(self, is_valid: bool, error_message: str = "", 
                 sanitized_value: Any = None, error_field: str = ""):
        """
        Initialize validation result.
        
        Args:
            is_valid: Whether validation passed
            error_message: Error message if failed
            sanitized_value: Cleaned value if valid
            error_field: Field name for focus management
        """
        self.is_valid = is_valid
        self.error_message = error_message
        self.sanitized_value = sanitized_value
        self.error_field = error_field
    
    def __bool__(self):
        """Allow using result in boolean context (if result:)"""
        return self.is_valid
    
    def __repr__(self):
        """String representation for debugging"""
        if self.is_valid:
            return f"ValidationResult(valid, value={self.sanitized_value})"
        else:
            return f"ValidationResult(invalid, error='{self.error_message}', field='{self.error_field}')"
    
    @staticmethod
    def success(value: Any, field: str = ""):
        """Create a successful validation result."""
        return ValidationResult(True, "", value, field)
    
    @staticmethod
    def error(message: str, field: str = ""):
        """Create a failed validation result."""
        return ValidationResult(False, message, None, field)


class InputValidation:
    """Pure validation class for user input. All methods are static."""
    
    @staticmethod
    def validate_amount(new_value):
        """
        Validate currency amount input for tkinter Entry validation.
        
        Allows digits and one decimal point, max 2 decimal places.
        Empty values are allowed (user is still typing).
        
        Args:
            new_value: Proposed value for Entry field
            
        Returns:
            True if valid, False otherwise
        """
        if new_value == "":
            return True
        
        if not all(c.isdigit() or c == '.' for c in new_value):
            return False
        
        if new_value.count('.') > 1:
            return False
        
        if '.' in new_value:
            parts = new_value.split('.')
            if len(parts) > 1 and len(parts[1]) > 2:
                return False
        
        try:
            if new_value != '.':
                float(new_value)
        except ValueError:
            return False
        
        return True
    
    @staticmethod
    def validate_final_amount(value_str):
        """
        Validate final amount value before form submission.
        
        More strict than validate_amount() - requires complete, valid, positive number.
        Rounds to 2 decimal places.
        
        Args:
            value_str: Amount string to validate
            
        Returns:
            ValidationResult with sanitized_value (float) if valid, error_message if invalid
        """
        if not value_str or value_str.strip() == "":
            return ValidationResult.error("Amount is required", "amount")
        
        try:
            amount = float(value_str.strip())
        except ValueError:
            return ValidationResult.error("Amount must be a valid number", "amount")
        
        if amount <= 0:
            return ValidationResult.error("Amount must be greater than 0", "amount")
        
        if amount >= 10000000:
            return ValidationResult.error("Amount is too large (max: $9,999,999.99)", "amount")
        
        amount_rounded = round(amount, 2)
        
        return ValidationResult.success(amount_rounded, "amount")
    
    @staticmethod
    def validate_description(value_str, max_length=100):
        """
        Validate expense description.
        
        Must not be empty/whitespace and must not exceed max_length.
        Strips leading/trailing whitespace.
        
        Args:
            value_str: Description string to validate
            max_length: Maximum allowed length (default: 100)
            
        Returns:
            ValidationResult with sanitized_value (stripped string) if valid
        """
        if not value_str or value_str.strip() == "":
            return ValidationResult.error("Description is required", "description")
        
        desc_stripped = value_str.strip()
        
        if len(desc_stripped) > max_length:
            return ValidationResult.error(
                f"Description is too long (max {max_length} characters)", 
                "description"
            )
        
        return ValidationResult.success(desc_stripped, "description")
    
    @staticmethod
    def parse_amount(value_str):
        """Parse amount string to float. Returns None if parsing fails."""
        try:
            return float(value_str.strip())
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def format_amount(amount):
        """Format amount for display with 2 decimal places."""
        return f"{amount:.2f}"
    
    @staticmethod
    def validate_expense_form(amount_str, description_str, date_str=None):
        """
        Validate complete expense form with all fields.
        
        Returns first error encountered, or success with dict of sanitized values.
        Uses today's date if date_str is None.
        
        Args:
            amount_str: Amount string to validate
            description_str: Description string to validate
            date_str: Date string (optional, uses today if None)
            
        Returns:
            ValidationResult with sanitized_value dict: {'amount': float, 'description': str, 'date': str}
        """
        from datetime import datetime
        
        amount_result = InputValidation.validate_final_amount(amount_str)
        if not amount_result:
            return amount_result
        
        desc_result = InputValidation.validate_description(description_str)
        if not desc_result:
            return desc_result
        
        if date_str is None or date_str.strip() == "":
            date_value = datetime.now().strftime("%Y-%m-%d")
        else:
            date_value = date_str.strip()
        
        sanitized_data = {
            'amount': amount_result.sanitized_value,
            'description': desc_result.sanitized_value,
            'date': date_value
        }
        
        return ValidationResult.success(sanitized_data, "form")


class ValidationPresets:
    """Pre-configured validation patterns for common form scenarios."""
    
    @staticmethod
    def quick_add_expense(amount_str, description_str):
        """Validate Quick Add expense form (uses today's date)."""
        return InputValidation.validate_expense_form(
            amount_str, 
            description_str, 
            None  # Uses today's date
        )
    
    @staticmethod
    def manual_add_expense(amount_str, description_str, date_str):
        """Validate Add Expense form with custom date."""
        return InputValidation.validate_expense_form(
            amount_str, 
            description_str, 
            date_str
        )
    
    @staticmethod
    def edit_expense(amount_str, description_str, date_str):
        """Validate Edit Expense form (all fields required)."""
        return InputValidation.validate_expense_form(
            amount_str, 
            description_str, 
            date_str
        )

