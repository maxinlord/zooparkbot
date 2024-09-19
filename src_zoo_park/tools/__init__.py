from .animals import (
    get_all_animals,
    get_price_animal,
    get_income_animal,
    get_dict_animals,
    get_numbers_animals,
    add_animal,
    get_total_number_animals,
    get_random_animal,
    get_animal_with_random_rarity,
    gen_quantity_animals,
    get_average_price_animals,
)

from .aviaries import (
    get_name_and_code_name,
    get_total_number_seats,
    get_remain_seats,
    add_aviary,
    get_price_aviaries,
)

from .bank import (
    get_rate,
    update_bank_storage,
    exchange,
    get_weight_rate_bank,
    get_increase_rate_bank,
)
from .base import (
    gen_key,
    find_integers,
    fetch_and_parse_str_value,
    get_events_list,
    sort_events_batch,
)

from .bonus import (
    referral_bonus,
    referrer_bonus,
    bonus_for_sub_on_channel,
    bonus_for_sub_on_chat,
    get_bonus,
    apply_bonus,
    DataBonus,
)

from .deep_link import validate_command_arg
from .game import (
    get_amount_gamers,
    get_total_moves_game,
    get_user_where_max_score,
    get_nickname_owner_game,
    get_first_three_places,
    get_gamer,
    gamer_have_active_game,
)
from .grafics import get_plot
from .income import income_

from .items import (
    get_animal_probability,
    gen_name_and_emoji_item,
    gen_price_to_create_item,
    gen_rarity_item,
    get_borders_property,
    get_items_data_for_merge_to_kb,
    get_items_data_for_up_to_kb,
    get_items_data_to_kb,
    get_property_probability,
    get_rarity_animal_probability,
    get_rarity_by_amount_props,
    get_row_items_for_kb,
    get_size_items_for_kb,
    get_value_prop_from_iai,
    calculate_percent_to_enhance,
    calculate_weight_merge,
    choice_prop,
    count_page_items,
    create_item,
    able_to_enhance,
    add_item_to_db,
    synchronize_info_about_items,
    random_up_property_item,
    update_prop_iai,
    merge_items
)

from .message import disable_not_main_window, m_choice_quantity_avi
from .nickname import (
    is_unique_nickname,
    shorten_whitespace_nickname,
    has_special_characters_nickname,
    view_nickname,
)
from .photo import get_photo, get_photo_from_message
from .plug_classes import UnityPlug
from .random_merchant import create_random_merchant, gen_price
from .referrals import get_referrals, get_verify_referrals

from .text import (
    get_text_message,
    get_text_button,
    mention_html,
    mention_html_by_username,
    factory_text_main_top,
    factory_text_unity_top,
    factory_text_top_mini_game,
    factory_text_main_top_by_money,
    factory_text_main_top_by_animals,
    factory_text_main_top_by_referrals,
    factory_text_account_animals,
    factory_text_account_aviaries,
    ft_bank_exchange_info,
    ft_bonus_info,
    ft_item_props,
    ft_item_props_for_update,
    contains_any_pattern
)

from .transfer import in_used, add_user_to_used
from .unity import (
    get_top_unity_by_animal,
    is_unique_name,
    get_unity_name_and_idpk,
    get_row_unity_for_kb,
    get_row_unity_members,
    get_size_unity_for_kb,
    get_size_unity_members,
    check_condition_1st_lvl,
    check_condition_2nd_lvl,
    check_condition_3rd_lvl,
    count_income_unity,
    count_page_unity,
    count_page_unity_members,
    has_special_characters_name,
    get_data_by_lvl_unity,
    shorten_whitespace_name_unity,
    get_members_name_and_idpk,
    fetch_unity,
    get_unity_idpk,
)

from .user import (
    get_currency,
    add_to_amount_expenses_currency,
    add_to_currency,
    fetch_users_for_top,
)
from .value import get_value
