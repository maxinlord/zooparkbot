from .text import get_text_message, get_text_button, mention_html
from .nickname import (
    has_special_characters_nickname,
    is_unique_nickname,
    shorten_whitespace_nickname,
)
from .deep_link import validate_command_arg
from .bonus import referral_bonus, referrer_bonus
from .random_merchant import (
    create_random_merchant,
    calculate_price_with_discount,
    gen_quantity_animals,
    gen_price,
    get_animal_with_random_rarity,
    get_random_animal
)
from .animals import (
    add_animal,
    get_all_animals,
    get_all_quantity_animals,
)
