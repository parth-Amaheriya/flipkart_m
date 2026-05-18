"""
Parser for Flipkart product page JSON responses.
Extracts important product-related data using .get() for safe dict access.
"""

import json
import os
from typing import Any, Dict, List, Optional


def _safe_get(data: Any, *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dicts using .get() chain."""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return default
    return data if data is not None else default


def _safe_get_from_list(items: List[Dict], index: int, *keys: str, default: Any = None) -> Any:
    """Safely get value from a list item at index, then traverse keys."""
    if isinstance(items, list) and 0 <= index < len(items):
        return _safe_get(items[index], *keys, default=default)
    return default


def _find_slot_by_viewtype(slots: List[Dict], view_type: str) -> Optional[Dict]:
    """Find a slot/widget by its viewType."""
    for slot in (slots or []):
        widget = slot.get("widget", {})
        if widget.get("viewType") == view_type:
            return widget
    return None


def _find_slot_by_widget_name(slots: List[Dict], widget_name: str) -> Optional[Dict]:
    """Find a slot/widget by its widgetName."""
    for slot in (slots or []):
        widget = slot.get("widget", {})
        if widget.get("widgetName") == widget_name:
            return widget
    return None


def _find_all_slots_by_viewtype(slots: List[Dict], view_type: str) -> List[Dict]:
    """Find all slots/widgets matching a viewType."""
    result = []
    for slot in (slots or []):
        widget = slot.get("widget", {})
        if widget.get("viewType") == view_type:
            result.append(widget)
    return result


def parse_breadcrumb(data: Dict) -> Dict:
    """Extract breadcrumb/category information from slot with viewType='breadcrumb'."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    widget = _find_slot_by_viewtype(slots, "breadcrumb")
    
    result = {}
    if widget:
        tracking = widget.get("tracking", {})
        dls_data = _safe_get(widget, "data", "dlsData", default={})
        
        result["category"] = tracking.get("category")
        result["sub_category"] = tracking.get("subCategory")
        result["super_category"] = tracking.get("superCategory")
        result["vertical"] = tracking.get("vertical")
        
        # Get breadcrumb product name from label_2
        result["breadcrumb_name"] = _safe_get(dls_data, "label_2", "value", "text")
    
    return result


def parse_product_title(data: Dict) -> Dict:
    """Extract product title and brand name from slot with viewType='default_fk_pp_productTitle'."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    widget = _find_slot_by_viewtype(slots, "default_fk_pp_productTitle")
    
    result = {}
    if widget:
        dls_data = _safe_get(widget, "data", "dlsData", default={})
        
        # Product title text
        result["product_title"] = _safe_get(dls_data, "customEllipsisData_0", "value", "prependingText")
        
        # Brand name
        result["brand"] = _safe_get(dls_data, "label_3", "value", "text")
    
    return result


def parse_rating(data: Dict) -> Dict:
    """Extract rating information from rating widget."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    widget = _find_slot_by_viewtype(slots, "default_fk_pp_multimedia_rating_clone")
    if not widget:
        widget = _find_slot_by_widget_name(slots, "ATLAS_RATING_INLINE_SLIDER_WITHOUT_SPOTLIGHT")
    
    result = {}
    if widget:
        dls_data = _safe_get(widget, "data", "dlsData", default={})
        rating_data = _safe_get(dls_data, "ratingData_0", "value", default={})
        
        result["rating"] = rating_data.get("rating")
        
        # Parse review count text (e.g. "| 2,882")
        review_text = rating_data.get("reviewText", "")
        if review_text:
            # Remove leading '| ' and commas
            cleaned = review_text.lstrip("| ").replace(",", "").replace("+", "")
            try:
                result["review_count"] = int(cleaned)
            except (ValueError, TypeError):
                result["review_count"] = None
    
    return result


def _resolve_state_value(state_obj: Any) -> Any:
    """
    Resolve values that may be wrapped in state-based structure (LOCKED/UNLOCKED).
    Returns the preferred value: UNLOCKED > LOCKED > direct value.
    """
    if isinstance(state_obj, dict):
        # Check for state-rule structure with LOCKED/UNLOCKED keys
        unlocked = state_obj.get("UNLOCKED")
        locked = state_obj.get("LOCKED")
        
        if unlocked is not None:
            # Recursively resolve the unlocked state
            if isinstance(unlocked, dict):
                text_val = _safe_get(unlocked, "value", "text")
                if text_val is not None:
                    return text_val
            return unlocked
        
        if locked is not None:
            if isinstance(locked, dict):
                text_val = _safe_get(locked, "value", "text")
                if text_val is not None:
                    return text_val
            return locked
    
    # If it's a dict but not a state-rule, try to get 'text' directly
    if isinstance(state_obj, dict):
        text_val = _safe_get(state_obj, "value", "text")
        if text_val is not None:
            return text_val
        # Return dict as-is if it has meaningful keys
        if any(k in state_obj for k in ("text", "url", "rating")):
            return state_obj
    
    return state_obj


def _clean_price_text(text: str) -> Optional[int]:
    """Clean price text string (e.g. '₹80', '₹100') and convert to int."""
    if not text or not isinstance(text, str):
        return None
    try:
        return int(text.replace("₹", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def parse_pricing(data: Dict) -> Dict:
    """Extract pricing information from price_with_tag widget."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    widget = _find_slot_by_viewtype(slots, "price_with_tag")
    
    result = {}
    if widget:
        dls_data = _safe_get(widget, "data", "dlsData", default={})
        price_desc = _safe_get(dls_data, "price_description_0", "value", default={})
        xtrasaver = _safe_get(dls_data, "xtrasaver_price_0", "value", default={})
        offer_deal = _safe_get(dls_data, "offer_deal_0", "value", default={})
        
        # MRP (original price) - direct value
        mrp_text = _safe_get(price_desc, "label_1", "value", "text")
        result["mrp"] = _clean_price_text(mrp_text)
        
        # Discount percentage - may be state-ruled (LOCKED/UNLOCKED)
        discount_obj = _safe_get(price_desc, "label_0", "value", default={})
        discount_text = _resolve_state_value(discount_obj)
        result["discount_percentage"] = discount_text if isinstance(discount_text, str) else None
        
        # XtraSaver price - may be state-ruled
        xs_obj = _safe_get(xtrasaver, "label_0", "value", default={})
        xs_price_text = _resolve_state_value(xs_obj)
        result["xtrasaver_price"] = _clean_price_text(xs_price_text) if isinstance(xs_price_text, str) else None
        
        # Locked price (non-XtraSaver price) - may be state-ruled
        locked_obj = _safe_get(price_desc, "label_2", "value", default={})
        locked_price_text = _resolve_state_value(locked_obj)
        result["selling_price"] = _clean_price_text(locked_price_text) if isinstance(locked_price_text, str) else None
        
        # XtraSaver savings
        savings_text = _safe_get(xtrasaver, "label_4", "value", "text")
        result["xtrasaver_savings"] = savings_text  # e.g. "₹4 saved"
        
        # Offer deal text
        offer_text = _safe_get(offer_deal, "label_0", "value", "text")
        result["offer_text"] = offer_text  # e.g. "₹0 off"
    
    return result


def parse_variants(data: Dict) -> List[Dict]:
    """Extract variant/quantity options from size-selector-view-wrapper widget."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    widget = _find_slot_by_viewtype(slots, "size-selector-view-wrapper")
    
    variants = []
    if widget:
        dls_data = _safe_get(widget, "data", "dlsData", default={})
        size_selector = _safe_get(dls_data, "size-selector-view_0", "value", default={})
        scroll_list = _safe_get(size_selector, "scrollToListData_0", "value", default=[])
        
        for item in (scroll_list or []):
            item_value = item.get("value", {}) if isinstance(item, dict) else {}
            variant = {
                "name": _safe_get(item_value, "label_0", "value", "text"),
                "unit_price": _safe_get(item_value, "label_4", "value", "text"),  # e.g. "(₹36/1L)"
                "product_id": _safe_get(item_value, "trackerData_0", "tracking", "productId"),
                "content_title": _safe_get(item_value, "trackerData_0", "tracking", "contentTitle"),
                "is_in_stock": "InStock" in str(_safe_get(item_value, "trackerData_0", "tracking", "contentType", default="")),
            }
            variants.append(variant)
        
        # Selected variant info from header
        selector_header = _safe_get(size_selector, "selector-header_0", "value", default={})
        result_selected = _safe_get(selector_header, "label_1", "value", "text")
        if result_selected:
            # Add selected variant info
            pass
    
    return variants


def parse_images(data: Dict) -> List[str]:
    """Extract product image URLs from multimedia inline slider widget."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    widget = _find_slot_by_viewtype(slots, "default_fk_pp_multimedia_inline_slider")
    
    images = []
    if widget:
        dls_data = _safe_get(widget, "data", "dlsData", default={})
        media_view = _safe_get(dls_data, "multiMediaViewData_0", "value", default=[])
        
        for item in (media_view or []):
            item_value = item.get("value", {}) if isinstance(item, dict) else {}
            img_url = _safe_get(item_value, "image_0", "value", "selected", "value", "dynamicImageUrl")
            if img_url:
                images.append(img_url)
    
    return images


def parse_product_specifications(data: Dict) -> Dict:
    """Extract product specifications from product-details-layout widget."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    widget = _find_slot_by_viewtype(slots, "product-details-layout")
    
    specs = {}
    if widget:
        dls_data = _safe_get(widget, "data", "dlsData", default={})
        details_grid = _safe_get(dls_data, "product-details-grid_0", "value", default={})
        grid_data = _safe_get(details_grid, "gridData_0", "value", default=[])
        
        for item in (grid_data or []):
            item_value = item.get("value", {}) if isinstance(item, dict) else {}
            label_text = _safe_get(item_value, "label_0", "value", "text")
            value_text = _safe_get(item_value, "label_1", "value", "text")
            
            if label_text and value_text:
                # Handle list type for value
                if isinstance(value_text, list):
                    value_text = ", ".join(value_text)
                specs[label_text] = value_text
    
    return specs


def parse_rpd_specifications(data: Dict) -> Dict:
    """Extract rich product details (RPD) specifications from rpd_all_details_showcase_vertical_list_layout widget."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    widget = _find_slot_by_viewtype(slots, "rpd_all_details_showcase_vertical_list_layout")
    
    specs = {}
    if widget:
        dls_data = _safe_get(widget, "data", "dlsData", default={})
        rpd_showcase = _safe_get(dls_data, "rpd_tab_showcase_vertical_list_0", "value", default={})
        
        # Specifications grid
        specs_grid = _safe_get(rpd_showcase, "rpd_specifications_grid_layout_1", "value", default={})
        grid_data = _safe_get(specs_grid, "gridData_0", "value", default=[])
        
        for section in (grid_data or []):
            section_value = section.get("value", {}) if isinstance(section, dict) else {}
            section_title = _safe_get(section_value, "label_0", "value", "text")
            
            rpd_grid = _safe_get(section_value, "rpd_grid_0", "value", default={})
            section_items = _safe_get(rpd_grid, "gridData_0", "value", default=[])
            
            for item in (section_items or []):
                item_value = item.get("value", {}) if isinstance(item, dict) else {}
                
                # Try multiple label keys for value
                label_text = _safe_get(item_value, "label_0", "value", "text")
                
                val_text = _safe_get(item_value, "label_2", "value", "text")
                if not val_text:
                    val_text = _safe_get(item_value, "label_1", "value", "text")
                
                if label_text and val_text:
                    if isinstance(val_text, list):
                        val_text = ", ".join(val_text)
                    if section_title:
                        specs[f"{section_title} > {label_text}"] = val_text
                    else:
                        specs[label_text] = val_text
        
        # Description
        description_item = _safe_get(rpd_showcase, "rpd_description_item_3", "value", default={})
        desc_text = _safe_get(description_item, "label_0", "value", "text")
        if desc_text:
            specs["Description"] = desc_text
        
        # Manufacturer info
        mfr_layout = _safe_get(rpd_showcase, "rpd_manufacture_layout_4", "value", default={})
        
        generic_name = _safe_get(mfr_layout, "default_fk_pp_rpd_header_body_0", "value", "label_1", "value", "text")
        if generic_name:
            if isinstance(generic_name, list):
                generic_name = ", ".join(generic_name)
            specs["Generic Name"] = generic_name
        
        country_of_origin = _safe_get(mfr_layout, "default_fk_pp_rpd_header_body_1", "value", "label_1", "value", "text")
        if country_of_origin:
            if isinstance(country_of_origin, list):
                country_of_origin = ", ".join(country_of_origin)
            specs["Country of Origin"] = country_of_origin
        
        manufacturer = _safe_get(mfr_layout, "default_fk_pp_rpd_header_body_2", "value", "label_1", "value", "text")
        if manufacturer:
            if isinstance(manufacturer, list):
                manufacturer = ", ".join(manufacturer)
            specs["Manufacturer"] = manufacturer
        
        importer = _safe_get(mfr_layout, "default_fk_pp_rpd_header_body_3", "value", "label_1", "value", "text")
        if importer:
            if isinstance(importer, list):
                importer = ", ".join(importer)
            specs["Importer"] = importer
        
        packer = _safe_get(mfr_layout, "default_fk_pp_rpd_header_body_4", "value", "label_1", "value", "text")
        if packer:
            if isinstance(packer, list):
                packer = ", ".join(packer)
            specs["Packer"] = packer
    
    return specs


def parse_product_id(data: Dict) -> Optional[str]:
    """Extract product ID from the first available tracking data."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    for slot in (slots or []):
        widget = slot.get("widget", {})
        tracking = widget.get("tracking", {})
        pid = tracking.get("productId")
        if pid:
            return pid
    return None


def parse_expiry_date(data: Dict) -> Optional[str]:
    """Extract expiry date from multimedia widget."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    widget = _find_slot_by_viewtype(slots, "default_fk_pp_multimedia_inline_slider")
    
    if widget:
        dls_data = _safe_get(widget, "data", "dlsData", default={})
        try_on_view = _safe_get(dls_data, "default_fk_pp_multimedia_try_on_view_similar_0", "value", default={})
        expiry_text = _safe_get(try_on_view, "label_3", "value", "text")
        return expiry_text
    
    return None


def parse_prescription_info(data: Dict) -> Dict:
    """Extract prescription requirement info."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    widget = _find_slot_by_viewtype(slots, "default_fk_pp_multimedia_inline_slider")
    
    result = {}
    if widget:
        dls_data = _safe_get(widget, "data", "dlsData", default={})
        rating_widget = _safe_get(dls_data, "default_fk_pp_multimedia_rating_0", "value", default={})
        
        prescript_text = _safe_get(rating_widget, "label_0", "value", "text")
        result["prescription_required"] = prescript_text  # "Prescription Required" or None
        
        # Rating from multimedia
        rating_data = _safe_get(rating_widget, "ratingData_0", "value", default={})
        result["multimedia_rating"] = rating_data.get("rating")
        result["multimedia_review_text"] = rating_data.get("reviewText")
    
    return result


def parse_share_info(data: Dict) -> Dict:
    """Extract sharing information."""
    slots = _safe_get(data, "RESPONSE", "slots", default=[])
    widget = _find_slot_by_viewtype(slots, "default_fk_pp_multimedia_inline_slider")
    
    result = {}
    if widget:
        dls_data = _safe_get(widget, "data", "dlsData", default={})
        wishlist_share = _safe_get(dls_data, "default_fk_pp_multimedia_wishlist_share_1", "value", default={})
        share_widget = _safe_get(wishlist_share, "default_fk_pp_multimedia_share_0", "value", default={})
        share_action = _safe_get(share_widget, "box_0", "action", default={})
        
        share_params = share_action.get("params", {})
        share_data = _safe_get(share_params, "data", default={}) if isinstance(share_params, dict) else {}
        
        result["share_text"] = share_data.get("shareText") if isinstance(share_data, dict) else None
        result["share_url"] = share_params.get("url") if isinstance(share_params, dict) else None
    
    return result


def parse_full_product_data(json_data: Dict) -> Dict:
    """
    Main function to parse all product data from Flipkart JSON response.
    Returns a consolidated dictionary of all extracted product information.
    """
    response = json_data.get("RESPONSE", {})
    slots = response.get("slots", [])
    
    breadcrumb = parse_breadcrumb(json_data)
    title_info = parse_product_title(json_data)
    rating_info = parse_rating(json_data)
    pricing = parse_pricing(json_data)
    variants = parse_variants(json_data)
    images = parse_images(json_data)
    specs = parse_product_specifications(json_data)
    rpd_specs = parse_rpd_specifications(json_data)
    prescription = parse_prescription_info(json_data)
    share = parse_share_info(json_data)
    
    product_id = parse_product_id(json_data)
    expiry = parse_expiry_date(json_data)
    
    # Merge specifications
    all_specs = {**specs, **rpd_specs}
    
    # Determine final selling price
    selling_price = pricing.get("selling_price") or pricing.get("xtrasaver_price")
    
    return {
        "product_id": product_id,
        "product_title": title_info.get("product_title"),
        "brand": title_info.get("brand") or breadcrumb.get("category"),
        "category": breadcrumb.get("category"),
        "sub_category": breadcrumb.get("sub_category"),
        "super_category": breadcrumb.get("super_category"),
        "vertical": breadcrumb.get("vertical"),
        "mrp": pricing.get("mrp"),
        "selling_price": selling_price,
        "discount_percentage": pricing.get("discount_percentage"),
        "xtrasaver_price": pricing.get("xtrasaver_price"),
        "xtrasaver_savings": pricing.get("xtrasaver_savings"),
        "offer_text": pricing.get("offer_text"),
        "rating": rating_info.get("rating"),
        "review_count": rating_info.get("review_count"),
        "expiry_date": expiry,
        "prescription_required": prescription.get("prescription_required"),
        "share_text": share.get("share_text"),
        "share_url": share.get("share_url"),
        "images": images,
        "variants": variants,
        "specifications": all_specs,
    }


def parse_json_file(data: Dict) -> Dict:
    # with open(filepath, "r", encoding="utf-8") as f:
    #     data = json.load(f)
    return parse_full_product_data(data)


# # ======================= CLI Usage =======================
# if __name__ == "__main__":
#     import sys
    
#     if len(sys.argv) > 1:
#         filepath = sys.argv[1]
#         if os.path.exists(filepath):
#             result = parse_json_file(filepath)

#             with open("parsed_product_data.json", "w", encoding="utf-8") as f:
#                 json.dump(result, f, indent=2, ensure_ascii=False)
#             print(json.dumps(result, indent=2, ensure_ascii=False))
#         else:
#             print(f"File not found: {filepath}")
#     else:
#         print("Usage: python parser.py <path_to_flipkart_json_file>")