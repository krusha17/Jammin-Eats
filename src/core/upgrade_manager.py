from src.core.constants import UPGRADE_DATA
from src.debug.logger import log


class UpgradeManager:
    """Manages the player's upgrades and applies their effects"""

    def __init__(self, owned=None):
        """Initialize the upgrade manager with an optional set of already owned upgrades"""
        self.owned = set(owned or [])
        log(f"UpgradeManager initialized with {len(self.owned)} owned upgrades")

    # ---------- Query methods ----------
    def has(self, upg_id):
        """Check if the player owns a specific upgrade"""
        return upg_id in self.owned

    def get_all_owned(self):
        """Return a list of all owned upgrades"""
        return list(self.owned)

    def get_all_available(self, include_owned=False):
        """Return a list of all available upgrades (prerequisites met)"""
        available = []
        for upg_id in UPGRADE_DATA:
            # Skip if already owned and we don't want to include owned
            if self.has(upg_id) and not include_owned:
                continue

            # Check prerequisites
            reqs = UPGRADE_DATA[upg_id].get("requires", [])
            if all(self.has(req) for req in reqs):
                available.append(upg_id)

        return available

    def affordable(self, upg_id, money):
        """Check if an upgrade is affordable and available for purchase"""
        # Already owned?
        if self.has(upg_id):
            return False

        # Valid upgrade?
        if upg_id not in UPGRADE_DATA:
            return False

        # Prerequisites met?
        reqs = UPGRADE_DATA[upg_id].get("requires", [])
        prereqs_met = all(self.has(req) for req in reqs)

        # Enough money?
        cost = UPGRADE_DATA[upg_id]["cost"]
        can_afford = money >= cost

        return prereqs_met and can_afford

    def get_details(self, upg_id):
        """Get detailed information about an upgrade"""
        if upg_id not in UPGRADE_DATA:
            return None

        upgrade = UPGRADE_DATA[upg_id].copy()
        # Add ownership status
        upgrade["owned"] = self.has(upg_id)
        return upgrade

    # ---------- Action methods ----------
    def buy(self, upg_id, money):
        """Attempt to buy an upgrade, returns the cost if successful, 0 otherwise"""
        if not self.affordable(upg_id, money):
            # Log why it's not affordable
            if self.has(upg_id):
                log(f"Cannot buy {upg_id}: Already owned")
            elif upg_id not in UPGRADE_DATA:
                log(f"[ERROR] Cannot buy {upg_id}: Invalid upgrade ID")
            else:
                reqs = UPGRADE_DATA[upg_id].get("requires", [])
                missing_reqs = [req for req in reqs if not self.has(req)]
                if missing_reqs:
                    req_names = [UPGRADE_DATA[req]["name"] for req in missing_reqs]
                    log(
                        f"Cannot buy {upg_id}: Missing prerequisites: {', '.join(req_names)}"
                    )
                else:
                    cost = UPGRADE_DATA[upg_id]["cost"]
                    log(
                        f"Cannot buy {upg_id}: Not enough money (costs ${cost}, have ${money})"
                    )
            return 0

        # Buy the upgrade
        cost = UPGRADE_DATA[upg_id]["cost"]
        self.owned.add(upg_id)
        upgrade_name = UPGRADE_DATA[upg_id]["name"]
        log(f"Purchased upgrade: {upgrade_name} for ${cost}")
        return cost

    def apply_upgrades(self, game):
        """Apply all owned upgrades to the game instance"""
        # Initialize base values
        player_speed_mul = 1.0
        max_stock = game.constants.MAX_STOCK
        food_lifespan_bonus = 0.0
        patience_mul = 1.0

        # Apply modifiers from owned upgrades
        for upg_id in self.owned:
            if upg_id not in UPGRADE_DATA:
                log(f"[ERROR] Unknown upgrade ID in owned upgrades: {upg_id}")
                continue

            mods = UPGRADE_DATA[upg_id]["mod"]

            # Apply speed multiplier (stacks multiplicatively)
            if "speed_mul" in mods:
                player_speed_mul *= mods["speed_mul"]
                log(f"Applied speed multiplier: {mods['speed_mul']}x from {upg_id}")

            # Apply inventory capacity bonus (stacks additively)
            if "max_stock" in mods:
                max_stock += mods["max_stock"]
                log(f"Applied max stock bonus: +{mods['max_stock']} from {upg_id}")

            # Apply food lifespan bonus (stacks additively)
            if "food_lifespan" in mods:
                food_lifespan_bonus += mods["food_lifespan"]
                log(
                    f"Applied food lifespan bonus: +{mods['food_lifespan']}s from {upg_id}"
                )

            # Apply patience multiplier (stacks multiplicatively)
            if "patience_mul" in mods:
                patience_mul *= mods["patience_mul"]
                log(
                    f"Applied patience multiplier: {mods['patience_mul']}x from {upg_id}"
                )

        # Update game attributes
        if game.player:
            game.player.speed_multiplier = player_speed_mul
            log(f"Set player speed multiplier to {player_speed_mul}x")

        game.max_stock = max_stock
        log(f"Set max stock to {max_stock}")

        game.food_lifespan_bonus = food_lifespan_bonus
        log(f"Set food lifespan bonus to +{food_lifespan_bonus}s")

        game.patience_multiplier = patience_mul
        log(f"Set patience multiplier to {patience_mul}x")

        return {
            "player_speed_mul": player_speed_mul,
            "max_stock": max_stock,
            "food_lifespan_bonus": food_lifespan_bonus,
            "patience_mul": patience_mul,
        }
