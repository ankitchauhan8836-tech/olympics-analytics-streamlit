"""Static lookups shared across the app."""

MEDALS = ["Gold", "Silver", "Bronze"]

MEDAL_COLORS = {
    "Gold": "#D4AF37",
    "Silver": "#A8A9AD",
    "Bronze": "#CD7F32",
    "No Medal": "#C9D1D9",
}

# Olympic ring palette
BLUE, YELLOW, BLACK, GREEN, RED = "#0085C7", "#F4C300", "#1B1B1B", "#009F3D", "#DF0024"

# A few NOC codes are missing from noc_regions.csv
REGION_FIXES = {
    "SGP": "Singapore",
    "ROT": "Refugee Olympic Team",
    "TUV": "Tuvalu",
    "UNK": "Unknown",
}

# Not real countries: hidden from country pickers and excluded from the ML panel
NON_COUNTRIES = {"Individual Olympic Athletes", "Refugee Olympic Team", "Unknown"}

# Host country (as named in the `region` column) of every Summer edition in the
# dataset. 1906 (Intercalated Games) is left out on purpose.
# Note: "Germany" merges West/East Germany and "Russia" merges the USSR, so the
# 1972 and 1980 host effects are approximations.
HOSTS = {
    1896: "Greece", 1900: "France", 1904: "USA", 1908: "UK", 1912: "Sweden",
    1920: "Belgium", 1924: "France", 1928: "Netherlands", 1932: "USA",
    1936: "Germany", 1948: "UK", 1952: "Finland", 1956: "Australia",
    1960: "Italy", 1964: "Japan", 1968: "Mexico", 1972: "Germany",
    1976: "Canada", 1980: "Russia", 1984: "USA", 1988: "South Korea",
    1992: "Spain", 1996: "USA", 2000: "Australia", 2004: "Greece",
    2008: "China", 2012: "UK", 2016: "Brazil",
}

# The edition right after the dataset ends (used by the predictor)
NEXT_EDITION = (2020, "Japan")

# IOC (NOC) code -> ISO-3166 alpha-3, only where they differ. Historical NOCs
# are folded into today's country so the world map is continuous.
NOC_ISO_FIXES = {
    "ALG": "DZA", "ANG": "AGO", "ANT": "ATG", "ARU": "ABW", "ASA": "ASM",
    "BAH": "BHS", "BAN": "BGD", "BAR": "BRB", "BER": "BMU", "BHU": "BTN",
    "BIZ": "BLZ", "BOT": "BWA", "BRN": "BHR", "BRU": "BRN", "BUL": "BGR",
    "BUR": "BFA", "CAM": "KHM", "CAY": "CYM", "CGO": "COG", "CHA": "TCD",
    "CHI": "CHL", "CRC": "CRI", "CRO": "HRV", "DEN": "DNK", "ESA": "SLV",
    "FIJ": "FJI", "GAM": "GMB", "GBS": "GNB", "GEQ": "GNQ", "GER": "DEU",
    "GRE": "GRC", "GRN": "GRD", "GUA": "GTM", "GUI": "GIN", "HAI": "HTI",
    "HON": "HND", "INA": "IDN", "IRI": "IRN", "ISV": "VIR", "IVB": "VGB",
    "KOS": "XKX", "KSA": "SAU", "KUW": "KWT", "LAT": "LVA", "LBA": "LBY",
    "LES": "LSO", "LIB": "LBN", "MAD": "MDG", "MAS": "MYS", "MAW": "MWI",
    "MGL": "MNG", "MON": "MCO", "MRI": "MUS", "MTN": "MRT", "MYA": "MMR",
    "NCA": "NIC", "NED": "NLD", "NEP": "NPL", "NGR": "NGA", "NIG": "NER",
    "PAR": "PRY", "PHI": "PHL", "PLE": "PSE", "POR": "PRT", "PUR": "PRI",
    "RSA": "ZAF", "SAM": "WSM", "SEY": "SYC", "SIN": "SGP", "SKN": "KNA",
    "SLO": "SVN", "SOL": "SLB", "SRI": "LKA", "SUD": "SDN", "SUI": "CHE",
    "TAN": "TZA", "TGA": "TON", "TOG": "TGO", "TPE": "TWN", "UAE": "ARE",
    "URU": "URY", "VAN": "VUT", "VIE": "VNM", "VIN": "VCT", "ZAM": "ZMB",
    "ZIM": "ZWE",
    # historical -> modern
    "URS": "RUS", "EUN": "RUS", "RU1": "RUS", "FRG": "DEU", "GDR": "DEU",
    "EUA": "DEU", "TCH": "CZE", "BOH": "CZE", "YUG": "SRB", "SCG": "SRB",
    "YAR": "YEM", "YMD": "YEM", "RHO": "ZWE", "BIR": "MMR", "CEY": "LKA",
    "NBO": "MYS", "MAL": "MYS", "UAR": "EGY", "ZAI": "COD", "AHO": "CUW",
}
# NOCs that have no modern country to draw on a map
NO_ISO = {"ANZ", "IOA", "ROT", "UNK", "SAA", "WIF"}
