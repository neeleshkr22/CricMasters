"""
OVR (Overall Rating) Calculator
Provides role-weighted overall rating calculations for cricket players
"""

def calculate_ovr(player):
    """
    Calculate role-weighted OVR (Overall Rating) for a player
    
    Args:
        player (dict): Player dictionary with 'role', 'batting', and 'bowling' keys
        
    Returns:
        float: Calculated overall rating (0-100)
    """
    role = player.get('role', 'batsman')
    batting = player.get('batting', 0)
    bowling = player.get('bowling', 0)
    
    # Role-weighted calculations for more accurate representation
    if role == 'batsman':
        # Batsmen: 80% batting, 20% bowling
        ovr = (batting * 0.80) + (bowling * 0.20)
    elif role == 'bowler':
        # Bowlers: 20% batting, 80% bowling
        ovr = (batting * 0.20) + (bowling * 0.80)
    elif role == 'all_rounder':
        # All-rounders: 50% batting, 50% bowling (balanced)
        ovr = (batting * 0.50) + (bowling * 0.50)
    elif role == 'wicket_keeper':
        # Wicket-keepers: 75% batting, 25% bowling (batting focused with slight bonus)
        ovr = (batting * 0.75) + (bowling * 0.25)
    else:
        # Default: simple average
        ovr = (batting + bowling) / 2
    
    return round(ovr, 1)


def get_ovr_tier(ovr):
    """
    Get tier classification based on OVR
    
    Args:
        ovr (float): Overall rating
        
    Returns:
        str: Tier name (Elite/Great/Good/Average/Below Average)
    """
    if ovr >= 90:
        return "Elite"
    elif ovr >= 85:
        return "Great"
    elif ovr >= 80:
        return "Good"
    elif ovr >= 70:
        return "Average"
    else:
        return "Below Average"


def get_market_value(ovr):
    """
    Calculate market value based on OVR
    
    Args:
        ovr (float): Overall rating
        
    Returns:
        int: Market value in coins
    """
    if ovr >= 90:
        return 5000000  # 5M
    elif ovr >= 85:
        return 3000000  # 3M
    elif ovr >= 80:
        return 2000000  # 2M
    elif ovr >= 75:
        return 1500000  # 1.5M
    elif ovr >= 70:
        return 1000000  # 1M
    else:
        return 500000   # 500K


def format_ovr_display(player):
    """
    Format player OVR for display with tier
    
    Args:
        player (dict): Player dictionary
        
    Returns:
        str: Formatted string like "85.5 (Great)"
    """
    ovr = calculate_ovr(player)
    tier = get_ovr_tier(ovr)
    return f"{ovr:.1f} ({tier})"


def get_legendary_price(player):
    """
    Calculate legendary auction starting price based on OVR
    
    Args:
        player (dict): Player dictionary
        
    Returns:
        int: Starting price for legendary auctions
    """
    ovr = calculate_ovr(player)
    
    if ovr >= 95:
        return 50000000  # 50M
    elif ovr >= 90:
        return 30000000  # 30M
    elif ovr >= 85:
        return 20000000  # 20M
    else:
        return 10000000  # 10M
