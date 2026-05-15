"""
Delivery Fee Calculator based on Province
Automatically calculates delivery fee from shipping address
"""

# Province ranks and base fee
BASE_FEE_PER_RANK = 36

PROVINCE_RANKS = {
    'Laguna': 1, 'Rizal': 2, 'Quezon': 3, 'Batangas': 4, 'Cavite': 5,
    'Bulacan': 6, 'Pampanga': 7, 'Bataan': 8, 'Zambales': 9, 'Tarlac': 10,
    'Nueva Ecija': 11, 'Aurora': 12, 'Marinduque': 13, 'Camarines Norte': 14,
    'Camarines Sur': 15, 'Oriental Mindoro': 16, 'Occidental Mindoro': 17,
    'Albay': 18, 'Sorsogon': 19, 'Catanduanes': 20, 'Romblon': 21,
    'Masbate': 22, 'Palawan': 23, 'Pangasinan': 24, 'Nueva Vizcaya': 25,
    'Quirino': 26, 'Benguet': 27, 'La Union': 28, 'Ifugao': 29,
    'Mountain Province': 30, 'Isabela': 31, 'Ilocos Sur': 32, 'Abra': 33,
    'Kalinga': 34, 'Apayao': 35, 'Cagayan': 36, 'Ilocos Norte': 37,
    'Batanes': 38, 'Northern Samar': 39, 'Samar': 40, 'Eastern Samar': 41,
    'Leyte': 42, 'Southern Leyte': 43, 'Biliran': 44, 'Cebu': 45,
    'Bohol': 46, 'Siquijor': 47, 'Negros Oriental': 48, 'Negros Occidental': 49,
    'Guimaras': 50, 'Iloilo': 51, 'Capiz': 52, 'Aklan': 53, 'Antique': 54,
    'Dinagat Islands': 55, 'Surigao del Norte': 56, 'Camiguin': 57,
    'Misamis Oriental': 58, 'Agusan del Norte': 59, 'Surigao del Sur': 60,
    'Agusan del Sur': 61, 'Bukidnon': 62, 'Misamis Occidental': 63,
    'Lanao del Norte': 64, 'Lanao del Sur': 65, 'Davao de Oro': 66,
    'Davao del Norte': 67, 'Davao Oriental': 68, 'Davao del Sur': 69,
    'Davao Occidental': 70, 'Cotabato': 71, 'Maguindanao del Norte': 72,
    'Maguindanao del Sur': 73, 'Sultan Kudarat': 74, 'South Cotabato': 75,
    'Sarangani': 76, 'Zamboanga del Norte': 77, 'Zamboanga del Sur': 78,
    'Zamboanga Sibugay': 79, 'Basilan': 80, 'Sulu': 81, 'Tawi-Tawi': 82,
}

# City to Province mapping
CITY_TO_PROVINCE = {
    'Manila': 'Laguna', 'Quezon City': 'Laguna', 'Pasig': 'Rizal',
    'Makati': 'Cavite', 'Taguig': 'Cavite', 'Paranaque': 'Cavite',
    'Las Piñas': 'Cavite', 'Muntinlupa': 'Cavite', 'Marikina': 'Rizal',
    'San Juan': 'Rizal', 'Pateros': 'Rizal', 'Cainta': 'Rizal',
    'Antipolo': 'Rizal', 'Tanay': 'Rizal', 'Binangonan': 'Rizal',
    'Angono': 'Rizal', 'Rodriguez': 'Rizal', 'Baras': 'Rizal',
    'Morong': 'Rizal', 'Jala-Jala': 'Rizal', 'Montalban': 'Rizal',
    'Santa Cruz': 'Laguna', 'Lumban': 'Laguna', 'Cavinti': 'Laguna',
    'Majayjay': 'Laguna', 'Liliw': 'Laguna', 'Pagsanjan': 'Laguna',
    'Pangil': 'Laguna', 'Siniloan': 'Laguna', 'Binan': 'Laguna',
    'Cabuyao': 'Laguna', 'Calauan': 'Laguna', 'Kalayaan': 'Laguna',
    'Longos': 'Laguna', 'Nagcarlan': 'Laguna', 'Pakil': 'Laguna',
    'Pila': 'Laguna', 'San Pablo': 'Laguna', 'Santa Maria': 'Laguna',
    'Candelaria': 'Laguna', 'Famy': 'Laguna', 'San Pedro': 'Laguna',
    'Zamora': 'Laguna', 'Sta Rosa': 'Laguna', 'Santa Rosa': 'Laguna',
    'Amadeo': 'Cavite', 'Kawit': 'Cavite', 'Maragondon': 'Cavite',
    'Rosario': 'Cavite', 'Magallanes': 'Cavite', 'Naic': 'Cavite',
    'Noveleta': 'Cavite', 'Ternate': 'Cavite', 'Imus': 'Cavite',
    'Aguinaldo': 'Cavite', 'Bacoor': 'Cavite', 'Dasmariñas': 'Cavite',
    'Silang': 'Cavite', 'Tagaytay': 'Cavite', 'Mendez': 'Cavite',
    'Alfonso': 'Cavite', 'Indang': 'Cavite',
}


def extract_province_from_address(address):
    """Extract province from address string"""
    if not address:
        return None
    
    address_lower = address.lower()
    
    # Check for exact province name match
    for province in PROVINCE_RANKS.keys():
        if province.lower() in address_lower:
            return province
    
    # Check for city/municipality name match
    for city, province in CITY_TO_PROVINCE.items():
        if city.lower() in address_lower:
            return province
    
    # Common abbreviations
    abbreviations = {
        'lag': 'Laguna', 'ncr': 'Laguna', 'metro manila': 'Laguna',
        'mm': 'Laguna', 'rizal': 'Rizal', 'cavite': 'Cavite',
        'quezon': 'Quezon', 'bulacan': 'Bulacan', 'pampanga': 'Pampanga',
        'tarlac': 'Tarlac', 'batangas': 'Batangas', 'bataan': 'Bataan',
        'zambales': 'Zambales', 'nueva ecija': 'Nueva Ecija',
    }
    
    for abbr, province in abbreviations.items():
        if abbr in address_lower:
            return province
    
    return None


def calculate_delivery_fee(address):
    """Calculate delivery fee based on address"""
    province = extract_province_from_address(address)
    
    if not province:
        # Default to Laguna if province cannot be determined
        return 36.0
    
    rank = PROVINCE_RANKS.get(province, 1)
    return float(rank * BASE_FEE_PER_RANK)


def debug_address_parsing(address):
    """Debug method to check address parsing"""
    province = extract_province_from_address(address)
    fee = calculate_delivery_fee(address)
    return {
        'address': address,
        'extracted_province': province,
        'calculated_fee': fee
    }
