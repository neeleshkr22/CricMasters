"""
Database models for MongoDB
"""
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from config import MONGODB_URI, AUCTION_SETTINGS


class Database:
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(MONGODB_URI)
        self.db = self.client['cricket_bot']
        print("✅ Connected to MongoDB")
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("❌ Disconnected from MongoDB")
    
    # User Team Management
    async def get_user_team(self, user_id):
        """Get user's team"""
        return await self.db.teams.find_one({"user_id": str(user_id)})
    
    async def create_user_team(self, user_id, team_name, players):
        """Create or update user's team"""
        team_data = {
            "user_id": str(user_id),
            "team_name": team_name,
            "players": players,
            "budget_remaining": AUCTION_SETTINGS['initial_budget'],
            "matches_played": 0,
            "wins": 0,
            "losses": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.db.teams.update_one(
            {"user_id": str(user_id)},
            {"$set": team_data},
            upsert=True
        )
        return team_data
    
    async def update_user_team(self, user_id, players, budget_remaining):
        """Update user's team after auction"""
        await self.db.teams.update_one(
            {"user_id": str(user_id)},
            {
                "$set": {
                    "players": players,
                    "budget_remaining": budget_remaining,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    async def increment_matches_played(self, user_id):
        """Increment matches played count"""
        await self.db.teams.update_one(
            {"user_id": str(user_id)},
            {
                "$inc": {"matches_played": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
    
    async def update_match_result(self, user_id, won):
        """Update win/loss record"""
        field = "wins" if won else "losses"
        await self.db.teams.update_one(
            {"user_id": str(user_id)},
            {
                "$inc": {field: 1, "matches_played": 1},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        # Also update economy collection
        await self.db.economy.update_one(
            {"user_id": str(user_id)},
            {
                "$inc": {"matches_played": 1},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
    
    async def award_match_coins(self, user_id, amount, reason="Match reward"):
        """Award coins to user after match"""
        await self.db.economy.update_one(
            {"user_id": str(user_id)},
            {
                "$inc": {
                    "coins": amount,
                    "balance": amount,
                    "total_earned": amount if amount > 0 else 0
                },
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
    
    async def deduct_coins(self, user_id, amount, reason="Penalty"):
        """Deduct coins from user"""
        user = await self.get_economy_user(user_id)
        if user and user.get('coins', 0) >= amount:
            await self.db.economy.update_one(
                {"user_id": str(user_id)},
                {
                    "$inc": {
                        "coins": -amount,
                        "balance": -amount,
                        "total_spent": amount
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return True
        return False
    
    async def set_playing_xi(self, user_id, playing_xi):
        """Set user's playing XI"""
        await self.db.teams.update_one(
            {"user_id": str(user_id)},
            {
                "$set": {
                    "playing_xi": playing_xi,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
    
    async def get_playing_xi(self, user_id):
        """Get user's playing XI"""
        team = await self.db.teams.find_one({"user_id": str(user_id)})
        if team:
            return team.get("playing_xi", [])
        return []
    
    # Match History
    async def save_match(self, match_data):
        """Save match details"""
        match_data['created_at'] = datetime.utcnow()
        result = await self.db.matches.insert_one(match_data)
        return str(result.inserted_id)
    
    async def get_user_matches(self, user_id, limit=10):
        """Get user's recent matches"""
        cursor = self.db.matches.find(
            {"$or": [{"team1_user": str(user_id)}, {"team2_user": str(user_id)}]}
        ).sort("created_at", -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def get_user_stats(self, user_id):
        """Get comprehensive user statistics"""
        team = await self.get_user_team(user_id)
        if not team:
            return None
        
        matches = await self.get_user_matches(user_id, limit=100)
        
        stats = {
            "team_name": team.get("team_name", "Unknown"),
            "matches_played": team.get("matches_played", 0),
            "wins": team.get("wins", 0),
            "losses": team.get("losses", 0),
            "win_rate": 0,
            "total_runs": 0,
            "total_wickets": 0,
            "highest_score": 0,
            "best_bowling": {"wickets": 0, "runs": 999}
        }
        
        if stats['matches_played'] > 0:
            stats['win_rate'] = (stats['wins'] / stats['matches_played']) * 100
        
        # Calculate additional stats from matches
        for match in matches:
            try:
                if match.get('team1_user') == str(user_id):
                    score_str = match.get('team1_score', '0/0')
                    if isinstance(score_str, str) and '/' in score_str:
                        runs, wickets = score_str.split('/')
                        runs = int(runs)
                        wickets = int(wickets)
                        stats['total_runs'] += runs
                        stats['total_wickets'] += wickets
                        if runs > stats['highest_score']:
                            stats['highest_score'] = runs
                else:
                    score_str = match.get('team2_score', '0/0')
                    if isinstance(score_str, str) and '/' in score_str:
                        runs, wickets = score_str.split('/')
                        runs = int(runs)
                        wickets = int(wickets)
                        stats['total_runs'] += runs
                        stats['total_wickets'] += wickets
                        if runs > stats['highest_score']:
                            stats['highest_score'] = runs
            except (ValueError, AttributeError):
                continue
        
        return stats
    
    # Auction System
    async def create_auction(self, guild_id, players, admin_id):
        """Create a new auction"""
        auction_data = {
            "guild_id": str(guild_id),
            "admin_id": str(admin_id),
            "players": players,
            "current_player_index": 0,
            "status": "active",
            "participants": [],
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.auctions.insert_one(auction_data)
        return str(result.inserted_id)
    
    async def get_active_auction(self, guild_id):
        """Get active auction for a guild"""
        return await self.db.auctions.find_one({
            "guild_id": str(guild_id),
            "status": "active"
        })
    
    async def add_auction_participant(self, auction_id, user_id, username):
        """Add participant to auction"""
        from bson.objectid import ObjectId
        
        participant = {
            "user_id": str(user_id),
            "username": username,
            "budget": AUCTION_SETTINGS['initial_budget'],
            "players": []
        }
        
        await self.db.auctions.update_one(
            {"_id": ObjectId(auction_id)},
            {"$addToSet": {"participants": participant}}
        )
    
    async def place_bid(self, auction_id, user_id, amount):
        """Place a bid in auction"""
        from bson.objectid import ObjectId
        
        auction = await self.db.auctions.find_one({"_id": ObjectId(auction_id)})
        
        if not auction:
            return False, "Auction not found"
        
        current_player_index = auction.get('current_player_index', 0)
        player = auction['players'][current_player_index]
        
        current_bid = player.get('current_bid', 0)
        
        if amount <= current_bid:
            return False, f"Bid must be higher than current bid of ${current_bid:,}"
        
        # Check if user has enough budget
        participant = next(
            (p for p in auction['participants'] if p['user_id'] == str(user_id)),
            None
        )
        
        if not participant:
            return False, "You are not registered for this auction"
        
        if amount > participant['budget']:
            return False, f"Insufficient budget. You have ${participant['budget']:,}"
        
        # Update bid
        await self.db.auctions.update_one(
            {"_id": ObjectId(auction_id)},
            {
                "$set": {
                    f"players.{current_player_index}.current_bid": amount,
                    f"players.{current_player_index}.highest_bidder": str(user_id)
                }
            }
        )
        
        return True, f"Bid placed successfully! Current bid: ${amount:,}"
    
    async def close_current_bid(self, auction_id):
        """Close current bid and assign player to highest bidder"""
        from bson.objectid import ObjectId
        
        auction = await self.db.auctions.find_one({"_id": ObjectId(auction_id)})
        
        if not auction:
            return None
        
        current_player_index = auction.get('current_player_index', 0)
        player = auction['players'][current_player_index]
        
        highest_bidder = player.get('highest_bidder')
        winning_bid = player.get('current_bid', 0)
        
        if highest_bidder and winning_bid > 0:
            # Update participant's budget and players
            await self.db.auctions.update_one(
                {
                    "_id": ObjectId(auction_id),
                    "participants.user_id": highest_bidder
                },
                {
                    "$inc": {f"participants.$.budget": -winning_bid},
                    "$push": {f"participants.$.players": player}
                }
            )
        
        # Move to next player
        next_index = current_player_index + 1
        
        if next_index >= len(auction['players']):
            # Auction complete
            await self.db.auctions.update_one(
                {"_id": ObjectId(auction_id)},
                {"$set": {"status": "completed"}}
            )
            return None
        else:
            await self.db.auctions.update_one(
                {"_id": ObjectId(auction_id)},
                {"$set": {"current_player_index": next_index}}
            )
            return auction['players'][next_index]
    
    # Leaderboard
    async def get_leaderboard(self, guild_id=None, limit=10):
        """Get top players leaderboard"""
        query = {}
        if guild_id:
            # Would need to track guild_id in team data
            pass
        
        cursor = self.db.teams.find(query).sort("wins", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    # Economy System
    async def get_economy_user(self, user_id):
        """Get user's economy data (includes coins, items, stats)"""
        user = await self.db.economy.find_one({"user_id": str(user_id)})
        return user
    
    async def create_economy_user(self, user_id, starting_coins=50000):
        """Create new economy user with starting balance"""
        user_data = {
            "user_id": str(user_id),
            "coins": starting_coins,
            "balance": starting_coins,
            "total_earned": starting_coins,
            "total_spent": 0,
            "matches_played": 0,
            "matches_won": 0,
            "last_daily": None,
            "items": [],
            "boosts": [],
            "inventory": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await self.db.economy.insert_one(user_data)
        return user_data
    
    async def get_user_balance(self, user_id):
        """Get user's coin balance"""
        user = await self.db.economy.find_one({"user_id": str(user_id)})
        if not user:
            # Create new economy entry
            from config import ECONOMY_SETTINGS
            await self.db.economy.insert_one({
                "user_id": str(user_id),
                "balance": ECONOMY_SETTINGS['starting_balance'],
                "coins": ECONOMY_SETTINGS['starting_balance'],
                "total_earned": 0,
                "total_spent": 0,
                "last_daily": None,
                "items": [],
                "boosts": [],
                "created_at": datetime.utcnow()
            })
            return ECONOMY_SETTINGS['starting_balance']
        return user.get('balance', 0) or user.get('coins', 0)
    
    async def add_coins(self, user_id, amount, reason=""):
        """Add coins to user balance"""
        await self.db.economy.update_one(
            {"user_id": str(user_id)},
            {
                "$inc": {"balance": amount, "coins": amount, "total_earned": amount},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        # Log transaction
        await self.db.transactions.insert_one({
            "user_id": str(user_id),
            "amount": amount,
            "type": "earn",
            "reason": reason,
            "timestamp": datetime.utcnow()
        })
    
    async def remove_coins(self, user_id, amount, reason=""):
        """Remove coins from user balance"""
        balance = await self.get_user_balance(user_id)
        if balance < amount:
            return False
        
        await self.db.economy.update_one(
            {"user_id": str(user_id)},
            {
                "$inc": {"balance": -amount, "coins": -amount, "total_spent": amount},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        # Log transaction
        await self.db.transactions.insert_one({
            "user_id": str(user_id),
            "amount": -amount,
            "type": "spend",
            "reason": reason,
            "timestamp": datetime.utcnow()
        })
        
        return True
    
    async def update_user_balance(self, user_id, amount):
        """Update user balance by adding or subtracting amount"""
        await self.db.economy.update_one(
            {"user_id": str(user_id)},
            {
                "$inc": {"balance": amount, "coins": amount},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        # Log transaction
        transaction_type = "earn" if amount > 0 else "spend"
        await self.db.transactions.insert_one({
            "user_id": str(user_id),
            "amount": amount,
            "type": transaction_type,
            "reason": "Balance update",
            "timestamp": datetime.utcnow()
        })
    
    async def add_item_to_inventory(self, user_id, item_id, item_data):
        """Add item to user's inventory"""
        await self.db.economy.update_one(
            {"user_id": str(user_id)},
            {
                "$push": {
                    "items": {
                        "item_id": item_id,
                        "data": item_data,
                        "acquired_at": datetime.utcnow()
                    }
                }
            },
            upsert=True
        )
    
    async def get_user_inventory(self, user_id):
        """Get user's inventory"""
        user = await self.db.economy.find_one({"user_id": str(user_id)})
        return user.get('items', []) if user else []
    
    async def add_boost(self, user_id, boost_type, boost_value, duration):
        """Add temporary boost to user"""
        expiry = datetime.utcnow()
        from datetime import timedelta
        expiry += timedelta(days=duration)
        
        await self.db.economy.update_one(
            {"user_id": str(user_id)},
            {
                "$push": {
                    "boosts": {
                        "type": boost_type,
                        "value": boost_value,
                        "expiry": expiry
                    }
                }
            },
            upsert=True
        )
    
    async def get_active_boosts(self, user_id):
        """Get user's active boosts"""
        user = await self.db.economy.find_one({"user_id": str(user_id)})
        if not user:
            return []
        
        # Filter expired boosts
        active_boosts = []
        now = datetime.utcnow()
        for boost in user.get('boosts', []):
            if boost['expiry'] > now:
                active_boosts.append(boost)
        
        # Clean up expired boosts
        if len(active_boosts) < len(user.get('boosts', [])):
            await self.db.economy.update_one(
                {"user_id": str(user_id)},
                {"$set": {"boosts": active_boosts}}
            )
        
        return active_boosts
    
    async def claim_daily_reward(self, user_id):
        """Claim daily login reward"""
        user = await self.db.economy.find_one({"user_id": str(user_id)})
        
        if user and user.get('last_daily'):
            last_daily = user['last_daily']
            now = datetime.utcnow()
            
            # Check if 24 hours have passed
            if (now - last_daily).total_seconds() < 86400:
                return False, (86400 - (now - last_daily).total_seconds())
        
        from config import ECONOMY_SETTINGS
        await self.add_coins(user_id, ECONOMY_SETTINGS['daily_bonus'], "Daily reward")
        
        await self.db.economy.update_one(
            {"user_id": str(user_id)},
            {"$set": {"last_daily": datetime.utcnow()}},
            upsert=True
        )
        
        return True, ECONOMY_SETTINGS['daily_bonus']
    
    # Match Records
    async def record_match_result(self, user_id, won, stats):
        """Record detailed match result with stats"""
        await self.increment_matches_played(user_id)
        await self.update_match_result(user_id, won)
        
        # Award coins based on performance
        from config import ECONOMY_SETTINGS
        coins_earned = 0
        
        if won:
            coins_earned += ECONOMY_SETTINGS['win_reward']
        else:
            coins_earned += ECONOMY_SETTINGS['loss_reward']
        
        # Bonus for wickets
        if 'wickets' in stats:
            coins_earned += stats['wickets'] * ECONOMY_SETTINGS['wicket_bonus']
        
        # Bonus for runs
        if 'runs' in stats:
            if stats['runs'] >= 100:
                coins_earned += ECONOMY_SETTINGS['century_bonus']
            elif stats['runs'] >= 50:
                coins_earned += ECONOMY_SETTINGS['fifty_bonus']
        
        await self.add_coins(user_id, coins_earned, f"Match reward ({'Win' if won else 'Loss'})")
        
        return coins_earned
    
    # Legendary Auction
    async def create_legendary_auction(self, guild_id, legendary_players, admin_id):
        """Create legendary auction"""
        auction_data = {
            "guild_id": str(guild_id),
            "admin_id": str(admin_id),
            "players": legendary_players,
            "current_player_index": 0,
            "status": "active",
            "participants": [],
            "entry_fee": 5000,
            "type": "legendary",
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.legendary_auctions.insert_one(auction_data)
        return str(result.inserted_id)
    
    # Weekly/Monthly Leaderboard
    async def get_leaderboard_by_period(self, period='weekly', limit=10):
        """Get leaderboard for specific period"""
        now = datetime.utcnow()
        
        if period == 'weekly':
            from datetime import timedelta
            start_date = now - timedelta(days=7)
        elif period == 'monthly':
            from datetime import timedelta
            start_date = now - timedelta(days=30)
        else:
            start_date = datetime.min
        
        # Get users with matches in period
        pipeline = [
            {
                "$match": {
                    "updated_at": {"$gte": start_date}
                }
            },
            {
                "$sort": {"wins": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        cursor = self.db.teams.aggregate(pipeline)
        return await cursor.to_list(length=limit)
    
    async def award_leaderboard_prizes(self, period='weekly'):
        """Award prizes to top players"""
        from config import LEADERBOARD_SETTINGS
        
        prizes = LEADERBOARD_SETTINGS.get(f'{period}_prizes', {})
        leaderboard = await self.get_leaderboard_by_period(period, limit=len(prizes))
        
        awarded = []
        for idx, user_data in enumerate(leaderboard, 1):
            if idx in prizes:
                prize = prizes[idx]
                user_id = user_data['user_id']
                
                # Award coins
                await self.add_coins(user_id, prize['coins'], f"{period.title()} Prize - Rank {idx}")
                
                # Award pack
                if 'pack' in prize:
                    await self.add_item_to_inventory(user_id, prize['pack'], {'type': 'pack'})
                
                awarded.append({
                    'user_id': user_id,
                    'rank': idx,
                    'prize': prize
                })
        
        return awarded


# Global database instance
db = Database()
