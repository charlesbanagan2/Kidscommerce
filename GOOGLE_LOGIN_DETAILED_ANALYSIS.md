# 🔍 Google Login API Integration - Detailed Technical Analysis

**Analyzed:** May 18, 2026  
**Components:** Mobile App, Backend API, Supabase Database  
**Findings:** 5 Critical Issues in Backend Database Operations

---

## PART 1: MOBILE APP IMPLEMENTATION

### File: `login_screen.dart` (Lines 44-46)

**Google Sign-In Configuration:**
```dart
final GoogleSignIn _googleSignIn = GoogleSignIn(
  clientId: '668360708226-q79n83ttq956po4cj3pd5qig0thiqp6c.apps.googleusercontent.com',
);
```

**Client ID:** Valid Google OAuth 2.0 credential for Flutter

### Login Method: `_handleGoogleSignIn()` (Lines 174-246)

**Complete Flow:**

```dart
Future<void> _handleGoogleSignIn() async {
  setState(() {
    _isLoading = true;
    _errorMessage = null;
  });

  try {
    // Step 1: Google authentication
    final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
    if (googleUser == null) {
      // User cancelled
      if (mounted) {
        setState(() => _isLoading = false);
      }
      return;
    }

    // Step 2: Get tokens
    final GoogleSignInAuthentication googleAuth = 
        await googleUser.authentication;

    // Step 3: Send to backend
    final authProvider = context.read<AuthProvider>();
    final success = await authProvider.loginWithGoogle(
      googleAuth.idToken ?? '',
      googleAuth.accessToken ?? '',
    );

    // Step 4: Handle response
    if (!mounted) return;

    if (success && authProvider.isAuthenticated) {
      final userRole = authProvider.user!.role.toLowerCase();
      
      // Role-based navigation
      if (userRole == 'buyer' || userRole == 'rider') {
        // Refresh user data
        if (userRole == 'buyer') {
          final buyerProvider = context.read<BuyerProvider>();
          final cartProvider = context.read<CartProvider>();
          await buyerProvider.fetchOrders();
          await cartProvider.loadCart();
        }
        
        // Navigate
        if (mounted) {
          if (userRole == 'rider') {
            Navigator.pushNamedAndRemoveUntil(
              context,
              '/rider-dashboard',
              (route) => false,
            );
          } else {
            Navigator.pushNamedAndRemoveUntil(
              context,
              '/home',
              (route) => false,
            );
          }
        }
      } else {
        // Role not authorized
        await _googleSignIn.signOut();
        await authProvider.logout();
        if (mounted) {
          setState(() {
            _errorMessage = 'Only Buyer and Rider accounts can log in.';
            _isLoading = false;
          });
        }
      }
    } else {
      // Login failed
      await _googleSignIn.signOut();
      if (mounted) {
        setState(() {
          _errorMessage = authProvider.errorMessage ?? 'Google sign-in failed.';
          _isLoading = false;
        });
        _triggerShake();
      }
    }
  } catch (e) {
    await _googleSignIn.signOut();
    if (mounted) {
      setState(() {
        _errorMessage = 'An error occurred: ${e.toString()}';
        _isLoading = false;
      });
    }
  }
}
```

### Request Preparation

**Package:** `google_sign_in: ^6.1.4`

**Tokens obtained:**
- `idToken` - JWT from Google with user info
- `accessToken` - OAuth token for API calls

**Both sent to backend** in POST request

---

## PART 2: AUTH PROVIDER - TOKEN MANAGEMENT

### File: `auth_provider.dart` (Lines 192-250+)

**Method:** `loginWithGoogle(String idToken, String accessToken)`

```dart
Future<bool> loginWithGoogle(String idToken, String accessToken) async {
  _setLoading(true);
  _clearError();

  try {
    // Make API call
    final result = await ApiService.request(
      'POST',
      '/api/v1/google-login',
      body: {
        'id_token': idToken,
        'access_token': accessToken,
      },
    );

    debugPrint('=== GOOGLE LOGIN RESPONSE ===');
    debugPrint('Full result: $result');

    // Parse tokens
    final tokensData = result['tokens'] as Map<String, dynamic>?;
    debugPrint('Tokens data: $tokensData');

    if (tokensData != null) {
      // NEW FORMAT: tokens nested
      if (tokensData['access_token'] != null &&
          tokensData['refresh_token'] != null) {
        _tokens = AuthTokens(
          accessToken: tokensData['access_token'],
          refreshToken: tokensData['refresh_token'],
          expiresIn: tokensData['expires_in'] ?? 86400,
          issuedAt: DateTime.now(),
        );
        ApiService.setTokens(_tokens!.accessToken, _tokens!.refreshToken);
        debugPrint('✓ Tokens set from nested format');
      }
    } else if (result['access_token'] != null &&
               result['refresh_token'] != null) {
      // OLD FORMAT: tokens at top level
      _tokens = AuthTokens(
        accessToken: result['access_token'],
        refreshToken: result['refresh_token'],
        expiresIn: result['expires_in'] ?? 86400,
        issuedAt: DateTime.now(),
      );
      ApiService.setTokens(_tokens!.accessToken, _tokens!.refreshToken);
      debugPrint('✓ Tokens set from flat format');
    }

    // Extract user data
    final userData = result['user'] ?? result;
    debugPrint('User data: $userData');

    if (userData is Map<String, dynamic>) {
      _user = User.fromJson(userData);
      debugPrint('✓ User: ${_user?.fullName}, Role: ${_user?.role}');
    }

    _isAuthenticated = true;

    // Save to device
    await _saveData();

    notifyListeners();
    debugPrint('=== LOGIN COMPLETE ===');
    return true;
    
  } on ApiException catch (e) {
    debugPrint('❌ API Exception: ${e.message}');
    _setErrorMessage(e.message);
    return false;
  } catch (e) {
    debugPrint('❌ Exception: $e');
    _setErrorMessage('Login failed: $e');
    return false;
  } finally {
    _setLoading(false);
  }
}
```

**Token Storage:**
```dart
Future<void> _saveData() async {
  final prefs = await SharedPreferences.getInstance();
  if (_tokens != null) {
    await prefs.setString(_accessTokenKey, _tokens!.accessToken);
    await prefs.setString(_refreshTokenKey, _tokens!.refreshToken);
    await prefs.setInt('token_expires_in', _tokens!.expiresIn);
    await prefs.setString('token_issued_at', _tokens!.issuedAt.toIso8601String());
  }
  if (_user != null) {
    await prefs.setString(_userKey, jsonEncode(_user!.toJson()));
  }
}
```

---

## PART 3: BACKEND API ENDPOINT

### File: `backend/app.py`

**Route:** `/api/v1/google-login` (POST)

### Complete Implementation

```python
@app.route('/api/v1/google-login', methods=['POST'])
def api_v1_google_login():
    """Handle Google OAuth login for mobile app"""
    try:
        # Get tokens from request
        data = request.get_json() or {}
        id_token = (data.get('id_token') or '').strip()
        access_token = (data.get('access_token') or '').strip()
        
        # Validate inputs
        if not id_token:
            return jsonify({'success': False, 'error': 'id_token is required'}), 400
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 1: VALIDATE GOOGLE TOKEN
        # ═══════════════════════════════════════════════════════════════
        
        # Call Google's token info endpoint
        verify_url = 'https://oauth2.googleapis.com/tokeninfo'
        try:
            resp = requests.get(
                verify_url, 
                params={'id_token': id_token},
                timeout=15
            )
        except Exception as e:
            app.logger.error(f'Google token verification timeout: {e}')
            return jsonify({
                'success': False, 
                'error': 'Google authentication service timeout'
            }), 503
        
        # Check response
        if resp.status_code != 200:
            return jsonify({
                'success': False, 
                'error': 'Invalid Google id_token'
            }), 401
        
        # Parse token data
        try:
            info = resp.json() or {}
        except Exception:
            return jsonify({
                'success': False, 
                'error': 'Failed to parse Google token'
            }), 401
        
        # Extract information
        email = info.get('email', '').strip().lower()
        given_name = info.get('given_name', '').strip()
        family_name = info.get('family_name', '').strip()
        google_sub = info.get('sub', '')  # Unique Google user ID
        
        # Validate required fields
        if not email:
            return jsonify({
                'success': False, 
                'error': 'Google token missing email'
            }), 401
        
        if not google_sub:
            # ⚠️ ISSUE #5: Weak fallback
            google_sub = str(abs(hash(id_token)))  # Hash-based fallback
            app.logger.warning(f'No Google sub claim, using hash fallback for {email}')
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 2: LOOKUP OR CREATE USER
        # ═══════════════════════════════════════════════════════════════
        
        # Scenario A: OAuth record exists (returning user)
        oauth_record = OAuth.query.filter_by(
            provider='google',
            provider_user_id=google_sub,
        ).first()
        
        user = None
        
        if oauth_record:
            # Returning user
            user = oauth_record.user
            app.logger.info(f'Google login: returning user {email} (id={user.id})')
        
        else:
            # New or existing user - look up by email
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Scenario B: Brand new user
                user = User(
                    first_name=given_name,
                    last_name=family_name,
                    email=email,
                    password='google_oauth',  # Special marker
                    phone='',
                    address='',
                    role='buyer',  # Default role
                    status='pending',  # ⚠️ ISSUE #2: Needs approval
                    email_verified=True,  # Google verified
                )
                db.session.add(user)
                # ⚠️ ISSUE #1: FIRST COMMIT (risky!)
                db.session.commit()
                app.logger.info(f'Created new user {email} (id={user.id})')
            else:
                # Scenario C: Existing user, no OAuth mapping
                app.logger.info(f'Found existing user {email} (id={user.id})')
            
            # Create OAuth record
            oauth_record = OAuth(
                provider='google',
                provider_user_id=google_sub,
                user=user,
                token={},  # ⚠️ ISSUE #4: Empty token!
            )
            db.session.add(oauth_record)
            # ⚠️ ISSUE #1: SECOND COMMIT (very risky!)
            db.session.commit()
            app.logger.info(f'Created OAuth record for {email}')
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: APPROVAL GATE
        # ═══════════════════════════════════════════════════════════════
        
        # ⚠️ ISSUE #3: No error handling/rollback
        if user.status != 'active':
            return jsonify({
                'success': False,
                'error': 'Your account is pending admin approval. '
                         'Please wait for notification or contact support.'
            }), 403
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 4: GENERATE TOKENS
        # ═══════════════════════════════════════════════════════════════
        
        # Generate JWT tokens (implementation varies)
        access_token_jwt = generate_jwt_token(user.id, 'access')
        refresh_token_jwt = generate_jwt_token(user.id, 'refresh')
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 5: RETURN RESPONSE
        # ═══════════════════════════════════════════════════════════════
        
        return jsonify({
            'success': True,
            'tokens': {
                'access_token': access_token_jwt,
                'refresh_token': refresh_token_jwt,
                'expires_in': 86400,  # 24 hours
                'token_type': 'Bearer'
            },
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'fullName': f"{user.first_name} {user.last_name}",
                'role': user.role,
                'status': user.status,
                'phone': user.phone,
                'email_verified': bool(user.email_verified),
                'two_factor_enabled': bool(user.two_factor_enabled),
                'profile_picture': user.profile_picture,
            }
        }), 200
        
    except Exception as e:
        # ⚠️ ISSUE #3: No rollback!
        app.logger.exception(f'Google login error: {e}')
        return jsonify({
            'success': False,
            'error': f'Google login failed: {str(e)[:100]}'
        }), 500
```

---

## PART 4: CRITICAL ISSUES & SOLUTIONS

### Issue #1: Multiple Unprotected Database Commits

**Location:** Backend endpoint, creating new user

**Problem:**
```python
db.session.commit()  # ✓ User saved
db.session.commit()  # ✗ OAuth might fail -> orphaned user!
```

**Impact:** Orphaned user records with no way to login

**Solution:**
```python
try:
    with db.session.begin_nested():  # Start transaction
        db.session.add(user)
        db.session.flush()  # Get user.id without committing
        
        oauth_record = OAuth(
            provider='google',
            provider_user_id=google_sub,
            user=user,
            token={'access_token': access_token}
        )
        db.session.add(oauth_record)
        # Both added, but not committed yet
    
    db.session.commit()  # Single commit for both
    
except Exception:
    db.session.rollback()  # Roll back both changes
    raise
```

---

### Issue #2: New Users Start as "Pending"

**Location:** Backend endpoint, user creation

**Problem:**
```python
status='pending',  # Requires admin approval!
```

**User Experience:**
1. Tap "Sign in with Google"
2. Authenticate successfully
3. Get 403 Forbidden
4. Can't access app
5. Bad UX! 😞

**Solution:**
Trust Google's authentication for auto-approval:
```python
status='active',  # User authenticated with Google, trust that
email_verified=True,  # Google verified the email
```

---

### Issue #3: No Error Rollback

**Location:** Entire endpoint

**Problem:**
```python
try:
    # ... operations that might fail ...
except Exception as e:
    return jsonify({'error': str(e)}), 500
    # No rollback!
```

**Risk:** Partial saves, inconsistent database state

**Solution:**
```python
try:
    with db.session.begin():
        # ... all operations in transaction ...
        pass
except Exception:
    db.session.rollback()  # Auto-rolled back
    raise
```

---

### Issue #4: OAuth Token Not Stored

**Location:** OAuth record creation

**Problem:**
```python
oauth_record = OAuth(
    provider='google',
    provider_user_id=google_sub,
    token={},  # ⚠️ Empty!
)
```

**Impact:** Cannot make API calls on user's behalf later

**Solution:**
```python
oauth_record = OAuth(
    provider='google',
    provider_user_id=google_sub,
    user=user,
    token={
        'access_token': access_token,
        'id_token': id_token,
        'created_at': datetime.utcnow().isoformat()
    }
)
```

---

### Issue #5: Weak Google Sub Fallback

**Location:** Token parsing

**Problem:**
```python
if not google_sub:
    google_sub = str(abs(hash(id_token)))  # Hash collisions!
```

**Risk:**
- Hash values differ between Python sessions
- Collisions possible
- Different users might get same ID

**Solution:**
```python
if not google_sub:
    return jsonify({
        'error': 'Invalid Google token (missing sub claim)'
    }), 401

# Require valid Google sub
```

---

## PART 5: DATABASE SCHEMA

### Required Tables

#### user table
```sql
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(50) DEFAULT 'buyer',
    status VARCHAR(50) DEFAULT 'pending',
    password TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    profile_picture VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    ...
);

CREATE INDEX idx_user_email ON "user"(email);
CREATE INDEX idx_user_status ON "user"(status);
```

#### oauth table (CRITICAL)
```sql
CREATE TABLE "oauth" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    token JSONB,  -- Stores {access_token, id_token, etc.}
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    
    UNIQUE(provider, provider_user_id),
    INDEX idx_oauth_user_id (user_id),
    INDEX idx_oauth_provider (provider)
);
```

---

## PART 6: COMPLETE FIXED IMPLEMENTATION

```python
@app.route('/api/v1/google-login', methods=['POST'])
def api_v1_google_login():
    """Google OAuth login - FIXED VERSION"""
    try:
        data = request.get_json() or {}
        id_token = (data.get('id_token') or '').strip()
        access_token = (data.get('access_token') or '').strip()
        
        if not id_token:
            return jsonify({'error': 'id_token required'}), 400
        
        # Validate with Google
        resp = requests.get(
            'https://oauth2.googleapis.com/tokeninfo',
            params={'id_token': id_token},
            timeout=15
        )
        
        if resp.status_code != 200:
            return jsonify({'error': 'Invalid token'}), 401
        
        info = resp.json()
        email = (info.get('email') or '').strip().lower()
        google_sub = info.get('sub')
        
        if not email or not google_sub:
            return jsonify({'error': 'Invalid token format'}), 401
        
        # Single transaction for all operations
        try:
            with db.session.begin_nested():
                # Check if OAuth record exists
                oauth = OAuth.query.filter_by(
                    provider='google',
                    provider_user_id=google_sub
                ).first()
                
                if oauth:
                    user = oauth.user
                else:
                    # Lookup by email
                    user = User.query.filter_by(email=email).first()
                    
                    if not user:
                        # FIX #2: Auto-approve Google users
                        user = User(
                            email=email,
                            first_name=info.get('given_name', ''),
                            last_name=info.get('family_name', ''),
                            password='google_oauth',
                            role='buyer',
                            status='active',  # FIXED: auto-approve
                            email_verified=True  # FIXED: trust Google
                        )
                        db.session.add(user)
                        db.session.flush()  # Get user.id
                    
                    # FIX #1: Single transaction
                    # FIX #4: Store OAuth token
                    oauth = OAuth(
                        user_id=user.id,
                        provider='google',
                        provider_user_id=google_sub,
                        token={
                            'access_token': access_token,
                            'id_token': id_token,
                            'expires_in': 3600
                        }
                    )
                    db.session.add(oauth)
            
            # Single commit for everything
            db.session.commit()
            
        except Exception as e:
            # FIX #3: Rollback on error
            db.session.rollback()
            raise
        
        # Generate tokens
        access_jwt = generate_jwt_token(user.id)
        refresh_jwt = generate_refresh_token(user.id)
        
        return jsonify({
            'success': True,
            'tokens': {
                'access_token': access_jwt,
                'refresh_token': refresh_jwt,
                'expires_in': 86400
            },
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'status': user.status
            }
        }), 200
        
    except Exception as e:
        app.logger.exception('Google login error')
        return jsonify({'error': 'Login failed'}), 500
```

---

## Summary Table

| Issue | Severity | Impact | Fixed |
|-------|----------|--------|-------|
| Multiple commits | 🔴 Critical | Orphaned records | Use transactions |
| Pending approval | 🔴 Critical | Users can't login | Auto-approve |
| No rollback | 🔴 Critical | Inconsistent data | Transaction rollback |
| No OAuth token | 🟡 High | Can't use APIs | Store token |
| Weak sub fallback | 🟡 High | Collisions | Require sub |

