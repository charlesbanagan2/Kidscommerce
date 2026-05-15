class DeliveryFeeService {
  static const int _baseFeePerRank = 36;

  static const Map<String, int> _provinceRanks = {
    'Laguna': 1,
    'Rizal': 2,
    'Quezon': 3,
    'Batangas': 4,
    'Cavite': 5,
    'Bulacan': 6,
    'Pampanga': 7,
    'Bataan': 8,
    'Zambales': 9,
    'Tarlac': 10,
    'Nueva Ecija': 11,
    'Aurora': 12,
    'Marinduque': 13,
    'Camarines Norte': 14,
    'Camarines Sur': 15,
    'Oriental Mindoro': 16,
    'Occidental Mindoro': 17,
    'Albay': 18,
    'Sorsogon': 19,
    'Catanduanes': 20,
    'Romblon': 21,
    'Masbate': 22,
    'Palawan': 23,
    'Pangasinan': 24,
    'Nueva Vizcaya': 25,
    'Quirino': 26,
    'Benguet': 27,
    'La Union': 28,
    'Ifugao': 29,
    'Mountain Province': 30,
    'Isabela': 31,
    'Ilocos Sur': 32,
    'Abra': 33,
    'Kalinga': 34,
    'Apayao': 35,
    'Cagayan': 36,
    'Ilocos Norte': 37,
    'Batanes': 38,
    'Northern Samar': 39,
    'Samar': 40,
    'Eastern Samar': 41,
    'Leyte': 42,
    'Southern Leyte': 43,
    'Biliran': 44,
    'Cebu': 45,
    'Bohol': 46,
    'Siquijor': 47,
    'Negros Oriental': 48,
    'Negros Occidental': 49,
    'Guimaras': 50,
    'Iloilo': 51,
    'Capiz': 52,
    'Aklan': 53,
    'Antique': 54,
    'Dinagat Islands': 55,
    'Surigao del Norte': 56,
    'Camiguin': 57,
    'Misamis Oriental': 58,
    'Agusan del Norte': 59,
    'Surigao del Sur': 60,
    'Agusan del Sur': 61,
    'Bukidnon': 62,
    'Misamis Occidental': 63,
    'Lanao del Norte': 64,
    'Lanao del Sur': 65,
    'Davao de Oro': 66,
    'Davao del Norte': 67,
    'Davao Oriental': 68,
    'Davao del Sur': 69,
    'Davao Occidental': 70,
    'Cotabato': 71,
    'Maguindanao del Norte': 72,
    'Maguindanao del Sur': 73,
    'Sultan Kudarat': 74,
    'South Cotabato': 75,
    'Sarangani': 76,
    'Zamboanga del Norte': 77,
    'Zamboanga del Sur': 78,
    'Zamboanga Sibugay': 79,
    'Basilan': 80,
    'Sulu': 81,
    'Tawi-Tawi': 82,
  };

  /// Mapping of cities/municipalities to their provinces
  /// This helps when only city name is in the address
  static const Map<String, String> _cityToProvince = {
    // Metro Manila (treated as NCR - use Laguna as default/nearby)
    'Manila': 'Laguna',
    'Quezon City': 'Laguna',
    'Pasig': 'Rizal',
    'Makati': 'Cavite',
    'Taguig': 'Cavite',
    'Paranaque': 'Cavite',
    'Las Piñas': 'Cavite',
    'Muntinlupa': 'Cavite',
    'Marikina': 'Rizal',
    'San Juan': 'Rizal',
    'Pateros': 'Rizal',
    'Cainta': 'Rizal',
    'Antipolo': 'Rizal',
    'Tanay': 'Rizal',
    'Binangonan': 'Rizal',
    'Angono': 'Rizal',
    'Rodriguez': 'Rizal',
    'Baras': 'Rizal',
    'Morong': 'Rizal',
    'Jala-Jala': 'Rizal',
    'Montalban': 'Rizal',

    // Laguna
    'Santa Cruz': 'Laguna',
    'Lumban': 'Laguna',
    'Cavinti': 'Laguna',
    'Majayjay': 'Laguna',
    'Liliw': 'Laguna',
    'Pagsanjan': 'Laguna',
    'Pangil': 'Laguna',
    'Siniloan': 'Laguna',
    'Binan': 'Laguna',
    'Cabuyao': 'Laguna',
    'Calauan': 'Laguna',
    'Kalayaan': 'Laguna',
    'Longos': 'Laguna',
    'Nagcarlan': 'Laguna',
    'Pakil': 'Laguna',
    'Pila': 'Laguna',
    'San Pablo': 'Laguna',
    'Santa Maria': 'Laguna',
    'Candelaria': 'Laguna',
    'Castillejos': 'Laguna',
    'Famy': 'Laguna',
    'San Pedro': 'Laguna',
    'Zamora': 'Laguna',
    'Sta Rosa': 'Laguna',
    'Santa Rosa': 'Laguna',

    // Cavite
    'Amadeo': 'Cavite',
    'Kawit': 'Cavite',
    'Maragondon': 'Cavite',
    'Rosario': 'Cavite',
    'Magallanes': 'Cavite',
    'Naic': 'Cavite',
    'Noveleta': 'Cavite',
    'Ternate': 'Cavite',
    'Imus': 'Cavite',
    'Aguinaldo': 'Cavite',
    'Bacoor': 'Cavite',
    'Dasmariñas': 'Cavite',
    'Silang': 'Cavite',
    'Tagaytay': 'Cavite',
    'Mendez': 'Cavite',
    'Alfonso': 'Cavite',
    'Indang': 'Cavite',

    // Bulacan
    'Angat': 'Bulacan',
    'Balagtas': 'Bulacan',
    'Baliuag': 'Bulacan',
    'Bulacan': 'Bulacan',
    'Bustos': 'Bulacan',
    'Cabanatuan': 'Nueva Ecija',
    'Caloocan': 'Bulacan',

    // Isabela
    'Cordon': 'Isabela',
    'Ilagan': 'Isabela',
    'Cauayan': 'Isabela',
    'Roxas': 'Isabela',
    'San Isidro': 'Isabela',
    'Aurora': 'Isabela',
    'Gamu': 'Isabela',
    'San Agustin': 'Isabela',
    'San Guillermo': 'Isabela',

    // Leyte
    'Albuera': 'Leyte',
    'Baybay': 'Leyte',
    'Candoni': 'Leyte',
    'Capoocan': 'Leyte',
    'Hilongos': 'Leyte',
    'Inopacan': 'Leyte',
    'Jaro': 'Leyte',
    'Kananga': 'Leyte',
    'La Paz': 'Leyte',
    'Leyte': 'Leyte',
    'Mahagonoy': 'Leyte',
    'Matag-ob': 'Leyte',
    'Matalom': 'Leyte',
    'Palo': 'Leyte',
    'Tabango': 'Leyte',
    'Tolosa': 'Leyte',
    'Tunga': 'Leyte',

    // Other major cities
    'Cebu': 'Cebu',
    'Bohol': 'Bohol',
    'Davao': 'Davao del Sur',
    'Cagayan de Oro': 'Misamis Oriental',
    'Iloilo City': 'Iloilo',
  };

  /// Calculate delivery fee based on province
  static double calculateDeliveryFee(String province) {
    final rank = _provinceRanks[province] ?? 1;
    return (rank * _baseFeePerRank).toDouble();
  }

  /// Calculate total delivery fee for multiple items
  static double calculateTotalDeliveryFee(String province, int itemCount) {
    final feePerItem = calculateDeliveryFee(province);
    return feePerItem * itemCount;
  }

  /// Get province rank
  static int getProvinceRank(String province) {
    return _provinceRanks[province] ?? 1;
  }

  /// Get all provinces sorted by rank
  static List<String> getAllProvinces() {
    final provinces = _provinceRanks.keys.toList();
    provinces.sort((a, b) => _provinceRanks[a]!.compareTo(_provinceRanks[b]!));
    return provinces;
  }

  /// Check if province exists
  static bool isValidProvince(String province) {
    return _provinceRanks.containsKey(province);
  }

  /// Extract province from address string
  /// First tries to find exact province name, then tries city/municipality names
  static String? extractProvinceFromAddress(String? address) {
    if (address == null || address.isEmpty) return null;

    final addressLower = address.toLowerCase();

    // Step 1: Check for exact province name match (case-insensitive)
    for (final province in _provinceRanks.keys) {
      if (addressLower.contains(province.toLowerCase())) {
        return province;
      }
    }

    // Step 2: Check for city/municipality name match to find province
    for (final city in _cityToProvince.keys) {
      if (addressLower.contains(city.toLowerCase())) {
        return _cityToProvince[city];
      }
    }

    // Step 3: Common abbreviations and variations
    final abbreviations = {
      'lag': 'Laguna',
      'rizal': 'Rizal',
      'cavite': 'Cavite',
      'quezon': 'Quezon',
      'bulacan': 'Bulacan',
      'pampanga': 'Pampanga',
      'tarlac': 'Tarlac',
      'batangas': 'Batangas',
      'bataan': 'Bataan',
      'zambales': 'Zambales',
      'nueva ecija': 'Nueva Ecija',
      'ncr': 'Laguna', // Metro Manila defaults to nearby Laguna
      'metro manila': 'Laguna',
      'mm': 'Laguna',
    };

    for (final abbr in abbreviations.keys) {
      if (addressLower.contains(abbr)) {
        return abbreviations[abbr];
      }
    }

    return null; // No province found
  }

  /// Get delivery fee from address (extracts province automatically)
  static double calculateDeliveryFeeFromAddress(String? address) {
    final province = extractProvinceFromAddress(address);
    if (province == null) {
      // Default to Laguna if province cannot be determined
      return 36.0;
    }
    return calculateDeliveryFee(province);
  }

  /// Calculate total delivery fee from address
  static double calculateTotalDeliveryFeeFromAddress(
      String? address, int itemCount) {
    final feePerItem = calculateDeliveryFeeFromAddress(address);
    return feePerItem * itemCount;
  }

  /// Debug method to check address parsing
  static Map<String, dynamic> debugAddressParsing(String? address) {
    return {
      'address': address,
      'extractedProvince': extractProvinceFromAddress(address),
      'calculatedFee': calculateDeliveryFeeFromAddress(address),
    };
  }
}
