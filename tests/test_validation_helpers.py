"""Unit tests for validation helper functions in api/drone_router.py"""
import pytest
from fastapi import HTTPException
from api.drone_router import (
    validate_part_name,
    validate_status,
    validate_tree_number,
    validate_confidence,
    VALID_PARTS,
    VALID_STATUSES
)


class TestValidatePartName:
    """Test part_name validation and normalization."""
    
    def test_valid_parts(self):
        """Valid parts should pass."""
        for part in VALID_PARTS:
            assert validate_part_name(part) == part
    
    def test_normalize_uppercase(self):
        """Uppercase parts should normalize to lowercase."""
        assert validate_part_name("STEM") == "stem"
        assert validate_part_name("BUD") == "bud"
        assert validate_part_name("LEAVES") == "leaves"
    
    def test_normalize_mixed_case(self):
        """Mixed case should normalize to lowercase."""
        assert validate_part_name("Stem") == "stem"
        assert validate_part_name("sTEM") == "stem"
    
    def test_normalize_with_whitespace(self):
        """Whitespace should be stripped."""
        assert validate_part_name("  stem  ") == "stem"
        assert validate_part_name("  BUD  ") == "bud"
    
    def test_invalid_part_raises_error(self):
        """Invalid parts should raise HTTPException with 400."""
        with pytest.raises(HTTPException) as exc_info:
            validate_part_name("INVALID_PART")
        assert exc_info.value.status_code == 400
        assert "Invalid part_name" in exc_info.value.detail
    
    def test_empty_part_raises_error(self):
        """Empty part_name should raise HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_part_name("")
        assert exc_info.value.status_code == 400


class TestValidateStatus:
    """Test status validation and normalization."""
    
    def test_valid_statuses(self):
        """Valid statuses should pass."""
        for status in VALID_STATUSES:
            assert validate_status(status) == status
    
    def test_normalize_uppercase_statuses(self):
        """Uppercase statuses should normalize."""
        assert validate_status("HEALTHY") == "healthy"
        assert validate_status("UNHEALTHY") == "unhealthy"
        assert validate_status("CRITICAL") == "critical"
    
    def test_normalize_disease_statuses(self):
        """Disease statuses should normalize."""
        assert validate_status("BUD_ROT") == "bud_rot"
        assert validate_status("STEM_BLEEDING") == "stem_bleeding"
        assert validate_status("BUD_ROOT_DROPPING") == "bud_root_dropping"
    
    def test_invalid_status_raises_error(self):
        """Invalid status should raise HTTPException with 400."""
        with pytest.raises(HTTPException) as exc_info:
            validate_status("INVALID_STATUS")
        assert exc_info.value.status_code == 400
        assert "Invalid status" in exc_info.value.detail
    
    def test_empty_status_raises_error(self):
        """Empty status should raise HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_status("")
        assert exc_info.value.status_code == 400


class TestValidateTreeNumber:
    """Test tree_number validation."""
    
    def test_positive_tree_numbers(self):
        """Positive tree numbers should pass."""
        assert validate_tree_number(1) == 1
        assert validate_tree_number(10) == 10
        assert validate_tree_number(999) == 999
    
    def test_zero_tree_number_raises_error(self):
        """Zero tree_number should raise HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_tree_number(0)
        assert exc_info.value.status_code == 400
        assert "positive integer" in exc_info.value.detail
    
    def test_negative_tree_number_raises_error(self):
        """Negative tree_number should raise HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_tree_number(-1)
        assert exc_info.value.status_code == 400
        assert "positive integer" in exc_info.value.detail
    
    def test_false_value_raises_error(self):
        """Falsy values (0, None, False) should raise error."""
        with pytest.raises(HTTPException):
            validate_tree_number(None)


class TestValidateConfidence:
    """Test confidence validation and type conversion."""
    
    def test_valid_confidence_range(self):
        """Confidence in 0.0-1.0 should pass."""
        assert validate_confidence(0.0) == 0.0
        assert validate_confidence(0.5) == 0.5
        assert validate_confidence(1.0) == 1.0
        assert validate_confidence(0.95) == 0.95
    
    def test_convert_string_to_float(self):
        """String confidence should convert to float."""
        assert validate_confidence("0.95") == 0.95
        assert validate_confidence("0.5") == 0.5
        assert validate_confidence("1.0") == 1.0
    
    def test_convert_int_to_float(self):
        """Integer confidence should convert to float."""
        assert validate_confidence(0) == 0.0
        assert validate_confidence(1) == 1.0
    
    def test_out_of_range_high_raises_error(self):
        """Confidence > 1.0 should raise HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_confidence(1.5)
        assert exc_info.value.status_code == 400
        assert "0.0-1.0" in exc_info.value.detail
    
    def test_out_of_range_low_raises_error(self):
        """Confidence < 0.0 should raise HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_confidence(-0.1)
        assert exc_info.value.status_code == 400
        assert "0.0-1.0" in exc_info.value.detail
    
    def test_invalid_string_raises_error(self):
        """Non-numeric string should raise HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_confidence("invalid")
        assert exc_info.value.status_code == 400
        assert "must be a number" in exc_info.value.detail
