from .text import get_text_message, get_text_button, mention_html
from .nickname import (
    has_special_characters_nickname,
    is_unique_nickname,
    shorten_whitespace_nickname,
)
from .deep_link import validate_command_arg
from .bonus import (
    referral_bonus,
    referrer_bonus,
    bonus_for_sub_on_channel,
    bonus_for_sub_on_chat,
    bonus
)
from .random_merchant import (
    create_random_merchant,
    calculate_price_with_discount,
    gen_quantity_animals,
    gen_price,
    get_animal_with_random_rarity,
    get_random_animal,
)
from .animals import (
    get_all_animals,
    get_quantity_animals_for_rmerchant,
    get_quantity_animals_for_rshop,
    get_price_animal,
    get_income_animal,
    get_top_unity_by_animal
)

from .items import (
    get_all_name_items,
    get_row_items_for_kb,
    get_size_items_for_kb,
    get_items_data_to_kb,
    count_page_items,
)
from .message import disable_not_main_window
from .aviaries import (
    get_all_name_aviaries,
    get_quantity_animals_for_avi,
    get_total_number_seats,
    get_remain_seats,
)
from .bank import get_rate_bank
from .income import income
from .unity import (
    is_unique_name,
    shorten_whitespace_name_unity,
    has_special_characters_name,
    get_row_unity_for_kb,
    get_size_unity_for_kb,
    get_unity_name_and_idpk,
    count_page_unity,
    check_condition_1st_lvl,
    check_condition_2nd_lvl,
    check_condition_3rd_lvl,
    get_data_by_lvl_unity,
    get_row_unity_members,
    get_size_unity_members,
    count_page_unity_members,
    get_members_name_and_idpk,
    factory_text_unity_top
)
from .top import factory_text_main_top
