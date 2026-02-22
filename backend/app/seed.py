"""
Idempotent seed script. Runs on every startup; uses insert-if-not-exists
semantics so re-runs are safe.
"""
import logging
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.models import ItemDefinition, ChecklistItem, BasketType, ItemFrequency

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Item definitions
# ---------------------------------------------------------------------------

BASIC_KIT_ITEMS = [
    # (name, category, has_expiration, recommended_qty, unit)
    # Wound Care
    ("Assorted adhesive bandages (variety sizes)", "Wound Care", False, 30, "pieces"),
    ("Steri-Strips", "Wound Care", True, 10, "strips"),
    ("Non-stick pads", "Wound Care", False, 10, "pieces"),
    ("Gauze 2x2", "Wound Care", False, 12, "pieces"),
    ("Gauze 4x4", "Wound Care", False, 12, "pieces"),
    ("Rolled gauze", "Wound Care", False, 4, "rolls"),
    ("Medical tape (paper)", "Wound Care", False, 2, "rolls"),
    ("Medical tape (cloth)", "Wound Care", False, 2, "rolls"),
    ("Liquid bandage", "Wound Care", True, 1, "bottle"),
    ("Hemostatic dressing (small pack)", "Wound Care", True, 1, "pack"),
    # Topicals
    ("Triple antibiotic ointment", "Topicals", True, 2, "tubes"),
    ("Hydrocortisone 1%", "Topicals", True, 1, "tube"),
    ("Antifungal cream", "Topicals", True, 1, "tube"),
    ("Burn gel", "Topicals", True, 1, "tube"),
    ("Lidocaine topical", "Topicals", True, 1, "tube"),
    ("Calamine lotion", "Topicals", True, 1, "bottle"),
    # Medications
    ("Acetaminophen", "Medications", True, 1, "bottle"),
    ("Ibuprofen", "Medications", True, 1, "bottle"),
    ("Aspirin (adult)", "Medications", True, 1, "bottle"),
    ("Diphenhydramine", "Medications", True, 1, "box"),
    ("Loratadine", "Medications", True, 1, "box"),
    ("Loperamide", "Medications", True, 1, "box"),
    ("Oral rehydration salts", "Medications", True, 2, "packets"),
    ("Electrolyte powder", "Medications", True, 6, "packets"),
    ("Glucose tabs", "Medications", True, 1, "tube"),
    ("Ondansetron ODT (if prescribed)", "Medications", True, 1, "pack"),
    # Assessment
    ("Digital thermometer", "Basic Assessment", False, 1, "unit"),
    ("Pulse oximeter", "Basic Assessment", False, 1, "unit"),
    ("BP cuff", "Basic Assessment", False, 1, "unit"),
    ("Stethoscope", "Basic Assessment", False, 1, "unit"),
    ("Penlight", "Basic Assessment", False, 1, "unit"),
    ("Trauma shears", "Basic Assessment", False, 1, "unit"),
    ("Tweezers", "Basic Assessment", False, 1, "unit"),
    ("Eye wash", "Basic Assessment", True, 1, "bottle"),
    ("Saline flush", "Basic Assessment", True, 4, "syringes"),
    ("Finger splint", "Basic Assessment", False, 2, "units"),
    ("Instant cold packs", "Basic Assessment", False, 4, "packs"),
    ("Nitrile gloves", "PPE", False, 10, "pairs"),
    ("CPR mask", "Basic Assessment", False, 1, "unit"),
]

ADVANCED_KIT_ITEMS = [
    # (name, sub_bin, category, has_expiration, recommended_qty, unit)
    # TRAUMA
    ("Tourniquet CAT or SOFT-T (x2)", "TRAUMA", "Bleeding Control", False, 2, "units"),
    ("Israeli pressure bandage", "TRAUMA", "Bleeding Control", False, 2, "units"),
    ("Hemostatic gauze (QuikClot/Celox)", "TRAUMA", "Bleeding Control", True, 2, "packs"),
    ("Chest seals (vented pair)", "TRAUMA", "Chest Injury", False, 1, "pair"),
    ("Occlusive dressing (backup)", "TRAUMA", "Chest Injury", False, 2, "units"),
    ("Trauma shears (heavy-duty)", "TRAUMA", "Tools", False, 1, "unit"),
    # WOUND
    ("Non-adherent dressings", "WOUND", "Wound Care", False, 10, "pieces"),
    ("Saline irrigation (500mL)", "WOUND", "Wound Care", True, 2, "bottles"),
    ("Irrigation syringe 60mL", "WOUND", "Wound Care", False, 2, "units"),
    ("Rolled gauze", "WOUND", "Wound Care", False, 4, "rolls"),
    ("Gauze 4x4 sterile", "WOUND", "Wound Care", False, 20, "pieces"),
    ("Medical tape", "WOUND", "Wound Care", False, 2, "rolls"),
    ("Triple antibiotic ointment", "WOUND", "Topicals", True, 2, "tubes"),
    # AIRWAY
    ("Oropharyngeal airways (assorted)", "AIRWAY", "Airway Management", False, 3, "units"),
    ("Nasopharyngeal airway + lubricant", "AIRWAY", "Airway Management", True, 1, "set"),
    ("Bag-valve mask (adult)", "AIRWAY", "Ventilation", False, 1, "unit"),
    ("Suction device (manual)", "AIRWAY", "Airway Management", False, 1, "unit"),
    # BURN
    ("Water gel dressings", "BURN", "Burn Care", True, 4, "units"),
    ("Non-adherent burn sheets", "BURN", "Burn Care", False, 2, "units"),
    ("Large sterile sheets", "BURN", "Burn Care", False, 2, "units"),
    ("Burn gel", "BURN", "Burn Care", True, 2, "tubes"),
    ("Emergency blankets", "BURN", "Burn Care", False, 2, "units"),
    # IMMOB
    ("SAM splints (full)", "IMMOB", "Immobilisation", False, 2, "units"),
    ("SAM splints (finger)", "IMMOB", "Immobilisation", False, 4, "units"),
    ("Triangular bandages", "IMMOB", "Immobilisation", False, 4, "units"),
    ("Elastic wraps", "IMMOB", "Immobilisation", False, 4, "rolls"),
    ("Pelvic binder", "IMMOB", "Immobilisation", False, 1, "unit"),
    # MEDS
    ("Aspirin 325mg chewable", "MEDS", "Medications", True, 1, "pack"),
    ("EpiPen (if prescribed)", "MEDS", "Medications", True, 2, "units"),
    ("Nitroglycerin (if prescribed)", "MEDS", "Medications", True, 1, "bottle"),
    ("Rescue inhaler (if prescribed)", "MEDS", "Medications", True, 1, "unit"),
    ("Electrolyte powder", "MEDS", "Medications", True, 6, "packets"),
    ("Glucose tabs", "MEDS", "Medications", True, 1, "tube"),
    # DX
    ("Pulse oximeter (backup)", "DX", "Diagnostics", False, 1, "unit"),
    ("ECG device (portable)", "DX", "Diagnostics", False, 1, "unit"),
    ("Extra ECG electrodes", "DX", "Diagnostics", True, 10, "sets"),
    ("Manual BP cuff", "DX", "Diagnostics", False, 1, "unit"),
    ("Stethoscope (cardiac grade)", "DX", "Diagnostics", False, 1, "unit"),
    ("Glucometer + strips + lancets", "DX", "Diagnostics", True, 1, "set"),
    ("Nebulizer", "DX", "Respiratory", False, 1, "unit"),
    ("Peak flow meter", "DX", "Respiratory", False, 1, "unit"),
    # PROCEDURE
    ("Sterile suture kit", "PROCEDURE", "Procedures", True, 1, "kit"),
    ("Skin stapler", "PROCEDURE", "Procedures", True, 1, "unit"),
    ("Lidocaine (if legal to store)", "PROCEDURE", "Procedures", True, 1, "vial"),
    ("Irrigation syringe 60mL", "PROCEDURE", "Procedures", False, 2, "units"),
    ("Sterile saline (large bottle)", "PROCEDURE", "Procedures", True, 1, "bottle"),
    ("Sterile drapes", "PROCEDURE", "Procedures", True, 2, "packs"),
    ("Sterile gloves", "PROCEDURE", "PPE", True, 4, "pairs"),
    # PPE
    ("Nitrile gloves (box)", "PPE", "PPE", False, 1, "box"),
    ("Eye protection (goggles)", "PPE", "PPE", False, 2, "pairs"),
    ("N95 masks", "PPE", "PPE", True, 10, "units"),
    ("Surgical masks", "PPE", "PPE", True, 20, "units"),
    # DOCS
    ("Emergency med forms", "DOCS", "Documentation", False, 5, "sheets"),
    ("Family medical history sheet", "DOCS", "Documentation", False, 1, "sheet"),
    ("Drug allergy list", "DOCS", "Documentation", False, 1, "sheet"),
    ("Notepad + waterproof pen", "DOCS", "Documentation", False, 1, "set"),
    ("Sharpie (for TQ time marking)", "DOCS", "Documentation", False, 2, "markers"),
    ("Protocol cards", "DOCS", "Documentation", False, 1, "set"),
    ("Emergency contacts", "DOCS", "Documentation", False, 1, "sheet"),
    # WATER
    ("Oral rehydration salts", "WATER", "Rehydration", True, 4, "packets"),
    ("Electrolyte powder", "WATER", "Rehydration", True, 6, "packets"),
    ("Clean water pouches", "WATER", "Rehydration", True, 6, "pouches"),
    # COMFORT
    ("Instant cold packs", "COMFORT", "Comfort", False, 4, "packs"),
    ("Heat packs", "COMFORT", "Comfort", False, 4, "packs"),
    ("Hydrocortisone 1% (anti-itch)", "COMFORT", "Comfort", True, 1, "tube"),
    ("Calamine lotion", "COMFORT", "Comfort", True, 1, "bottle"),
    ("Diphenhydramine", "COMFORT", "Comfort", True, 1, "box"),
]

# ---------------------------------------------------------------------------
# Cleaning checklist data
# format: (room, category, item_key, description, frequency, sort_order)
# ---------------------------------------------------------------------------

CHECKLIST_ITEMS = [
    # ---- KITCHEN ----
    ("kitchen", "Counters & Surfaces", "kitchen_wipe_counters", "Wipe down all countertops", ItemFrequency.DAILY, 1),
    ("kitchen", "Counters & Surfaces", "kitchen_clean_stovetop", "Clean stovetop and burners", ItemFrequency.DAILY, 2),
    ("kitchen", "Counters & Surfaces", "kitchen_clean_sink", "Clean and disinfect kitchen sink", ItemFrequency.DAILY, 3),
    ("kitchen", "Counters & Surfaces", "kitchen_wipe_appliances", "Wipe exterior of appliances (microwave, toaster, etc.)", ItemFrequency.WEEKLY, 4),
    ("kitchen", "Counters & Surfaces", "kitchen_clean_backsplash", "Scrub backsplash", ItemFrequency.WEEKLY, 5),
    ("kitchen", "Appliances", "kitchen_clean_microwave_inside", "Clean inside of microwave", ItemFrequency.WEEKLY, 6),
    ("kitchen", "Appliances", "kitchen_clean_fridge_outside", "Wipe refrigerator exterior and handles", ItemFrequency.WEEKLY, 7),
    ("kitchen", "Appliances", "kitchen_clean_fridge_inside", "Clean inside refrigerator, discard expired items", ItemFrequency.MONTHLY, 8),
    ("kitchen", "Appliances", "kitchen_clean_oven", "Deep clean oven inside", ItemFrequency.MONTHLY, 9),
    ("kitchen", "Appliances", "kitchen_descale_coffee", "Descale coffee maker", ItemFrequency.MONTHLY, 10),
    ("kitchen", "Floors & Drains", "kitchen_sweep_floor", "Sweep/vacuum kitchen floor", ItemFrequency.DAILY, 11),
    ("kitchen", "Floors & Drains", "kitchen_mop_floor", "Mop kitchen floor", ItemFrequency.WEEKLY, 12),
    ("kitchen", "Floors & Drains", "kitchen_clean_drain", "Clean sink drain and garbage disposal", ItemFrequency.WEEKLY, 13),
    ("kitchen", "Cabinets & Pantry", "kitchen_wipe_cabinet_doors", "Wipe cabinet and drawer fronts", ItemFrequency.WEEKLY, 14),
    ("kitchen", "Cabinets & Pantry", "kitchen_organize_pantry", "Organize pantry, check expiry dates", ItemFrequency.MONTHLY, 15),
    ("kitchen", "Seasonal Deep Clean", "kitchen_clean_under_appliances", "Clean under refrigerator and stove", ItemFrequency.SEASONAL, 16),
    ("kitchen", "Seasonal Deep Clean", "kitchen_clean_exhaust_fan", "Clean exhaust fan/range hood filter", ItemFrequency.SEASONAL, 17),
    ("kitchen", "Seasonal Deep Clean", "kitchen_replace_sponges", "Replace sponges and cleaning cloths", ItemFrequency.SEASONAL, 18),

    # ---- BATHROOM ----
    ("bathroom", "Toilet", "bathroom_clean_toilet_bowl", "Clean toilet bowl with brush", ItemFrequency.WEEKLY, 1),
    ("bathroom", "Toilet", "bathroom_wipe_toilet_exterior", "Wipe toilet exterior, lid, and handle", ItemFrequency.WEEKLY, 2),
    ("bathroom", "Toilet", "bathroom_disinfect_toilet", "Disinfect toilet seat and base", ItemFrequency.DAILY, 3),
    ("bathroom", "Sink & Vanity", "bathroom_clean_sink", "Clean and disinfect sink and faucet", ItemFrequency.DAILY, 4),
    ("bathroom", "Sink & Vanity", "bathroom_wipe_mirror", "Wipe and polish mirror", ItemFrequency.WEEKLY, 5),
    ("bathroom", "Sink & Vanity", "bathroom_organise_vanity", "Organize and wipe vanity surface", ItemFrequency.WEEKLY, 6),
    ("bathroom", "Shower & Tub", "bathroom_clean_shower_walls", "Scrub shower walls and door", ItemFrequency.WEEKLY, 7),
    ("bathroom", "Shower & Tub", "bathroom_clean_tub", "Scrub bathtub", ItemFrequency.WEEKLY, 8),
    ("bathroom", "Shower & Tub", "bathroom_scrub_grout", "Scrub tile grout", ItemFrequency.MONTHLY, 9),
    ("bathroom", "Shower & Tub", "bathroom_clean_shower_curtain", "Wash or replace shower curtain/liner", ItemFrequency.MONTHLY, 10),
    ("bathroom", "Floors & Walls", "bathroom_sweep_floor", "Sweep/vacuum bathroom floor", ItemFrequency.DAILY, 11),
    ("bathroom", "Floors & Walls", "bathroom_mop_floor", "Mop bathroom floor", ItemFrequency.WEEKLY, 12),
    ("bathroom", "Floors & Walls", "bathroom_wash_bath_mats", "Wash bath mats", ItemFrequency.WEEKLY, 13),
    ("bathroom", "Ventilation", "bathroom_clean_exhaust_fan", "Clean exhaust fan cover", ItemFrequency.SEASONAL, 14),
    ("bathroom", "Seasonal Deep Clean", "bathroom_clean_behind_toilet", "Clean behind and around toilet base", ItemFrequency.MONTHLY, 15),
    ("bathroom", "Seasonal Deep Clean", "bathroom_declutter_medicine", "Declutter medicine cabinet, check expiry", ItemFrequency.SEASONAL, 16),

    # ---- BEDROOM ----
    ("bedroom", "Bedding", "bedroom_make_bed", "Make bed", ItemFrequency.DAILY, 1),
    ("bedroom", "Bedding", "bedroom_wash_sheets", "Wash bed sheets and pillowcases", ItemFrequency.WEEKLY, 2),
    ("bedroom", "Bedding", "bedroom_wash_duvet", "Wash duvet cover", ItemFrequency.WEEKLY, 3),
    ("bedroom", "Bedding", "bedroom_wash_pillows", "Wash pillows", ItemFrequency.MONTHLY, 4),
    ("bedroom", "Bedding", "bedroom_flip_mattress", "Rotate/flip mattress", ItemFrequency.SEASONAL, 5),
    ("bedroom", "Surfaces", "bedroom_dust_surfaces", "Dust all furniture surfaces", ItemFrequency.WEEKLY, 6),
    ("bedroom", "Surfaces", "bedroom_wipe_nightstands", "Wipe down nightstands", ItemFrequency.WEEKLY, 7),
    ("bedroom", "Surfaces", "bedroom_clean_mirrors", "Clean mirrors", ItemFrequency.WEEKLY, 8),
    ("bedroom", "Floor", "bedroom_vacuum_floor", "Vacuum or sweep floor", ItemFrequency.WEEKLY, 9),
    ("bedroom", "Floor", "bedroom_mop_floor", "Mop hard floor", ItemFrequency.MONTHLY, 10),
    ("bedroom", "Closet", "bedroom_organise_closet", "Organize closet, return items to correct bins", ItemFrequency.MONTHLY, 11),
    ("bedroom", "Seasonal Deep Clean", "bedroom_wash_curtains", "Wash window curtains", ItemFrequency.SEASONAL, 12),
    ("bedroom", "Seasonal Deep Clean", "bedroom_clean_under_bed", "Vacuum under bed", ItemFrequency.MONTHLY, 13),
    ("bedroom", "Seasonal Deep Clean", "bedroom_dust_ceiling_fan", "Dust ceiling fan blades", ItemFrequency.MONTHLY, 14),

    # ---- LIBRARY ----
    ("library", "Books & Shelves", "library_dust_shelves", "Dust all bookshelves", ItemFrequency.WEEKLY, 1),
    ("library", "Books & Shelves", "library_wipe_book_covers", "Wipe down book covers on exposed shelves", ItemFrequency.MONTHLY, 2),
    ("library", "Books & Shelves", "library_reorganise_books", "Reorganize books, remove unused", ItemFrequency.SEASONAL, 3),
    ("library", "Furniture", "library_dust_furniture", "Dust desks, chairs, lamps", ItemFrequency.WEEKLY, 4),
    ("library", "Furniture", "library_wipe_desk", "Wipe down desk surface", ItemFrequency.DAILY, 5),
    ("library", "Electronics", "library_wipe_screens", "Clean computer/TV screens", ItemFrequency.WEEKLY, 6),
    ("library", "Electronics", "library_dust_electronics", "Dust electronics and cable management area", ItemFrequency.MONTHLY, 7),
    ("library", "Floor", "library_vacuum_floor", "Vacuum or sweep floor", ItemFrequency.WEEKLY, 8),
    ("library", "Floor", "library_clean_rugs", "Vacuum rugs / wash if possible", ItemFrequency.MONTHLY, 9),
    ("library", "Seasonal Deep Clean", "library_wash_curtains", "Wash curtains/blinds", ItemFrequency.SEASONAL, 10),
    ("library", "Seasonal Deep Clean", "library_clean_windows", "Clean windows inside and out", ItemFrequency.SEASONAL, 11),

    # ---- DINING ROOM ----
    ("dining_room", "Table & Chairs", "dining_wipe_table", "Wipe dining table", ItemFrequency.DAILY, 1),
    ("dining_room", "Table & Chairs", "dining_clean_chairs", "Wipe chair seats and backs", ItemFrequency.WEEKLY, 2),
    ("dining_room", "Table & Chairs", "dining_clean_chair_legs", "Clean chair legs and feet", ItemFrequency.MONTHLY, 3),
    ("dining_room", "Surfaces", "dining_dust_sideboard", "Dust sideboard or buffet", ItemFrequency.WEEKLY, 4),
    ("dining_room", "Surfaces", "dining_clean_light_fixture", "Clean dining light fixture", ItemFrequency.MONTHLY, 5),
    ("dining_room", "Floor", "dining_sweep_floor", "Sweep/vacuum floor", ItemFrequency.DAILY, 6),
    ("dining_room", "Floor", "dining_mop_floor", "Mop floor", ItemFrequency.WEEKLY, 7),
    ("dining_room", "Seasonal Deep Clean", "dining_wash_curtains", "Wash curtains", ItemFrequency.SEASONAL, 8),
    ("dining_room", "Seasonal Deep Clean", "dining_polish_furniture", "Polish wood furniture", ItemFrequency.SEASONAL, 9),

    # ---- GYM ----
    ("gym", "Equipment", "gym_wipe_equipment", "Wipe down all gym equipment with disinfectant", ItemFrequency.DAILY, 1),
    ("gym", "Equipment", "gym_clean_mats", "Clean exercise mats", ItemFrequency.WEEKLY, 2),
    ("gym", "Equipment", "gym_disinfect_handles", "Disinfect handles, bars, and grips", ItemFrequency.DAILY, 3),
    ("gym", "Equipment", "gym_inspect_equipment", "Inspect equipment for wear/damage", ItemFrequency.MONTHLY, 4),
    ("gym", "Floor", "gym_sweep_floor", "Sweep/vacuum gym floor", ItemFrequency.WEEKLY, 5),
    ("gym", "Floor", "gym_mop_floor", "Mop rubber flooring", ItemFrequency.WEEKLY, 6),
    ("gym", "Air & Smell", "gym_air_out_room", "Open windows to air out space", ItemFrequency.DAILY, 7),
    ("gym", "Air & Smell", "gym_wash_towels", "Wash gym towels", ItemFrequency.WEEKLY, 8),
    ("gym", "Seasonal Deep Clean", "gym_deep_clean_mats", "Deep clean foam/rubber mats", ItemFrequency.SEASONAL, 9),
    ("gym", "Seasonal Deep Clean", "gym_clean_fans", "Clean fans and air circulation units", ItemFrequency.SEASONAL, 10),

    # ---- PLAYROOM ----
    ("playroom", "Toys", "playroom_tidy_toys", "Tidy and return toys to bins", ItemFrequency.DAILY, 1),
    ("playroom", "Toys", "playroom_disinfect_toys", "Disinfect high-touch plastic toys", ItemFrequency.WEEKLY, 2),
    ("playroom", "Toys", "playroom_wash_soft_toys", "Wash soft/stuffed toys", ItemFrequency.MONTHLY, 3),
    ("playroom", "Toys", "playroom_cull_toys", "Donate or dispose of broken/outgrown toys", ItemFrequency.SEASONAL, 4),
    ("playroom", "Floor", "playroom_vacuum_floor", "Vacuum or sweep floor", ItemFrequency.DAILY, 5),
    ("playroom", "Floor", "playroom_mop_floor", "Mop hard floor", ItemFrequency.WEEKLY, 6),
    ("playroom", "Floor", "playroom_clean_rug", "Vacuum/wash area rug", ItemFrequency.MONTHLY, 7),
    ("playroom", "Surfaces", "playroom_wipe_surfaces", "Wipe all shelves, tables, door handles", ItemFrequency.WEEKLY, 8),
    ("playroom", "Seasonal Deep Clean", "playroom_wash_curtains", "Wash curtains/fabric items", ItemFrequency.SEASONAL, 9),

    # ---- HALLWAYS ----
    ("hallways", "Floor", "hallway_sweep_floor", "Sweep/vacuum hallway floor", ItemFrequency.DAILY, 1),
    ("hallways", "Floor", "hallway_mop_floor", "Mop hallway floor", ItemFrequency.WEEKLY, 2),
    ("hallways", "Floor", "hallway_clean_rug", "Clean or wash entry rug", ItemFrequency.MONTHLY, 3),
    ("hallways", "Walls & Surfaces", "hallway_wipe_switches", "Wipe light switches and door handles", ItemFrequency.WEEKLY, 4),
    ("hallways", "Walls & Surfaces", "hallway_wipe_baseboards", "Wipe baseboards", ItemFrequency.MONTHLY, 5),
    ("hallways", "Walls & Surfaces", "hallway_dust_wall_art", "Dust picture frames and wall art", ItemFrequency.MONTHLY, 6),
    ("hallways", "Closets", "hallway_organise_entry", "Organize entry closet/shoe rack", ItemFrequency.MONTHLY, 7),
    ("hallways", "Seasonal Deep Clean", "hallway_clean_windows", "Clean hallway windows", ItemFrequency.SEASONAL, 8),
    ("hallways", "Seasonal Deep Clean", "hallway_wash_curtains", "Wash hallway curtains", ItemFrequency.SEASONAL, 9),

    # ---- LAUNDRY ROOM ----
    ("laundry_room", "Machines", "laundry_wipe_washer_exterior", "Wipe washing machine exterior", ItemFrequency.WEEKLY, 1),
    ("laundry_room", "Machines", "laundry_clean_washer_drum", "Run washer self-clean cycle", ItemFrequency.MONTHLY, 2),
    ("laundry_room", "Machines", "laundry_clean_dryer_lint", "Clean dryer lint trap", ItemFrequency.DAILY, 3),
    ("laundry_room", "Machines", "laundry_clean_dryer_drum", "Wipe dryer drum interior", ItemFrequency.MONTHLY, 4),
    ("laundry_room", "Machines", "laundry_clean_dryer_vent", "Clean full dryer vent duct", ItemFrequency.SEASONAL, 5),
    ("laundry_room", "Machines", "laundry_clean_washer_gasket", "Clean washer door gasket/seal", ItemFrequency.WEEKLY, 6),
    ("laundry_room", "Floor & Surfaces", "laundry_sweep_floor", "Sweep/vacuum floor", ItemFrequency.WEEKLY, 7),
    ("laundry_room", "Floor & Surfaces", "laundry_mop_floor", "Mop floor", ItemFrequency.MONTHLY, 8),
    ("laundry_room", "Floor & Surfaces", "laundry_wipe_sink", "Clean laundry sink", ItemFrequency.WEEKLY, 9),
    ("laundry_room", "Supplies", "laundry_check_supplies", "Check detergent, softener, and stain remover levels", ItemFrequency.WEEKLY, 10),
    ("laundry_room", "Seasonal Deep Clean", "laundry_clean_cabinets", "Wipe inside storage cabinets", ItemFrequency.SEASONAL, 11),

    # ---- GARAGE ----
    ("garage", "Floor", "garage_sweep_floor", "Sweep garage floor", ItemFrequency.WEEKLY, 1),
    ("garage", "Floor", "garage_clean_oil_stains", "Treat and clean oil/grease stains", ItemFrequency.MONTHLY, 2),
    ("garage", "Floor", "garage_pressure_wash_floor", "Pressure wash garage floor", ItemFrequency.SEASONAL, 3),
    ("garage", "Organisation", "garage_organise_tools", "Organize tools and equipment", ItemFrequency.MONTHLY, 4),
    ("garage", "Organisation", "garage_dispose_hazardous", "Safely dispose of hazardous materials (old paint, etc.)", ItemFrequency.SEASONAL, 5),
    ("garage", "Organisation", "garage_clear_clutter", "Clear clutter and donation items", ItemFrequency.SEASONAL, 6),
    ("garage", "Safety", "garage_check_fire_ext", "Check fire extinguisher charge", ItemFrequency.SEASONAL, 7),
    ("garage", "Safety", "garage_inspect_smoke_detector", "Test smoke/CO detector", ItemFrequency.MONTHLY, 8),
    ("garage", "Seasonal Deep Clean", "garage_wipe_shelves", "Wipe storage shelves", ItemFrequency.SEASONAL, 9),
    ("garage", "Seasonal Deep Clean", "garage_clean_fridge", "Clean garage refrigerator (if applicable)", ItemFrequency.SEASONAL, 10),

    # ---- FAMILY ROOM ----
    ("family_room", "Surfaces", "family_dust_surfaces", "Dust all surfaces, shelves, and decor", ItemFrequency.WEEKLY, 1),
    ("family_room", "Surfaces", "family_wipe_remotes", "Clean TV remotes and game controllers", ItemFrequency.WEEKLY, 2),
    ("family_room", "Surfaces", "family_clean_tv_screen", "Clean TV/monitor screen", ItemFrequency.WEEKLY, 3),
    ("family_room", "Upholstery", "family_vacuum_sofa", "Vacuum sofa and cushions", ItemFrequency.WEEKLY, 4),
    ("family_room", "Upholstery", "family_wash_throw_blankets", "Wash throw blankets and pillow covers", ItemFrequency.MONTHLY, 5),
    ("family_room", "Upholstery", "family_deep_clean_sofa", "Deep clean sofa fabric/leather", ItemFrequency.SEASONAL, 6),
    ("family_room", "Floor", "family_vacuum_floor", "Vacuum or sweep floor", ItemFrequency.WEEKLY, 7),
    ("family_room", "Floor", "family_mop_floor", "Mop hard floors", ItemFrequency.MONTHLY, 8),
    ("family_room", "Floor", "family_clean_rug", "Vacuum/steam clean area rug", ItemFrequency.MONTHLY, 9),
    ("family_room", "Seasonal Deep Clean", "family_wash_curtains", "Wash curtains and window treatments", ItemFrequency.SEASONAL, 10),
    ("family_room", "Seasonal Deep Clean", "family_clean_fireplace", "Clean fireplace/mantel (if applicable)", ItemFrequency.SEASONAL, 11),
    ("family_room", "Seasonal Deep Clean", "family_dust_ceiling_fan", "Dust ceiling fan and light fixtures", ItemFrequency.MONTHLY, 12),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

async def run_seed():
    async with AsyncSessionLocal() as db:
        # Seed basic kit items
        for (name, category, has_exp, qty, unit) in BASIC_KIT_ITEMS:
            existing = await db.execute(
                select(ItemDefinition)
                .where(ItemDefinition.basket_type == BasketType.FIRST_AID_BASIC)
                .where(ItemDefinition.name == name)
            )
            if existing.scalar_one_or_none() is None:
                db.add(ItemDefinition(
                    basket_type=BasketType.FIRST_AID_BASIC,
                    name=name,
                    category=category,
                    has_expiration=has_exp,
                    recommended_qty=qty,
                    unit=unit,
                ))

        # Seed advanced kit items
        for (name, sub_bin, category, has_exp, qty, unit) in ADVANCED_KIT_ITEMS:
            existing = await db.execute(
                select(ItemDefinition)
                .where(ItemDefinition.basket_type == BasketType.FIRST_AID_ADVANCED)
                .where(ItemDefinition.name == name)
                .where(ItemDefinition.sub_bin == sub_bin)
            )
            if existing.scalar_one_or_none() is None:
                db.add(ItemDefinition(
                    basket_type=BasketType.FIRST_AID_ADVANCED,
                    sub_bin=sub_bin,
                    name=name,
                    category=category,
                    has_expiration=has_exp,
                    recommended_qty=qty,
                    unit=unit,
                ))

        # Seed checklist items
        for (room, category, item_key, description, freq, sort) in CHECKLIST_ITEMS:
            existing = await db.execute(
                select(ChecklistItem).where(ChecklistItem.item_key == item_key)
            )
            if existing.scalar_one_or_none() is None:
                db.add(ChecklistItem(
                    room_type=room,
                    category=category,
                    item_key=item_key,
                    description=description,
                    frequency=freq,
                    sort_order=sort,
                ))

        await db.commit()
    logger.info("Seed data loaded successfully")
