class LeagueRanks:
    def __init__(self, multiplier, reward, name, display_name, value) -> None:
        self.multiplier = multiplier
        self.reward = reward
        self.name = name
        self.display_name = display_name
        self.value = value

iron        = LeagueRanks(name="iron"         , value=0, display_name="Hierro",       multiplier=1.0,   reward=100.0)
bronze      = LeagueRanks(name="bronze"       , value=1, display_name="Bronce",       multiplier=1.5,   reward=150.0)
silver      = LeagueRanks(name="silver"       , value=2, display_name="Plata",        multiplier=1.6,   reward=200.0)
gold        = LeagueRanks(name="gold"         , value=3, display_name="Oro",          multiplier=1.7,   reward=250.0)
platinum    = LeagueRanks(name="platinum"     , value=4, display_name="Platino",      multiplier=1.8,   reward=300.0)
diamond     = LeagueRanks(name="diamond"      , value=5, display_name="Diamante",     multiplier=1.9,   reward=350.0)
master      = LeagueRanks(name="master"       , value=6, display_name="Maestro",      multiplier=2.0,   reward=400.0)
grandmaster = LeagueRanks(name="grandmaster"  , value=7, display_name="Gran Maestro", multiplier=2.5,   reward=450.0)
challenger  = LeagueRanks(name="challenger"   , value=8, display_name="Retador",      multiplier=3.0,   reward=500.0)

divisions = {"IV": 4, "III": 3, "II": 2, "I": 1}
tiers = [iron, bronze, silver, gold, platinum, diamond, master, grandmaster, challenger]

def get_user_tier(tier):
        match tier:
            case "iron":
                return iron
            case "bronze":
                return bronze
            case "silver":
                return silver
            case "gold":
                return gold
            case "platinum":
                return platinum
            case "diamond":
                return diamond
            case "master":
                return master
            case "grandmaster":
                return grandmaster
            case "challenger":
                return challenger
            case _:
                return False