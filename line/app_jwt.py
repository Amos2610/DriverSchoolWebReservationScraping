import jwt
from jwt.algorithms import RSAAlgorithm
import time

privateKey = {
  "alg": "RS256",
  "d": "VFpGS2Os4yzvR9xmeEc-VJe7b1GPWOukFRC-0_LlvuP7qsLCe9-zOqMlZcyok-DyQFRAWLa-W0hqEimjEK04UODskpvgrUneMYOz80pU_mUTDZr-BTHftX97t0w4TanqMpkKfcD5xiqUEQzHs4VER04EoA487rBgn5KAnDNQnHc973GxMLvHIJEkVHC9HC0WU3FmxnJl99oLAQ6DIcYB_XJiQJ9yngdStaYPMf3oYACRgV09E5ztibytbLfqtI-EO_RUZ0m2_pJC6T2KdXDu2FfJ8ruesjFeomYmX2GmLWitXbhgEAC6R865WpR6ffotuE6gxKBii7f3JNWzo98M8Q",
  "dp": "oQ_GIldVRSOMu02iMmY1aeJQo1FCO81bhVFC4HppAn1JExwi7eymuHCx-mHxdmyj9D0t8e9rFOSDqt8mFWMU_fGsR78PMqcYFaMnZIAYWWz-AdggA3-YC0q4cz9jl4vYHcqcmWc9PZWskMTx5waCG36Hl3GTScURn8_HCBdGIQE",
  "dq": "wfWq-GE3z407deMsViPeiQJAjxn1jk2w1_4zh75U01KEZWrK-17h4G-bgDX38D3zPrJziaCWia13_OnDhH2MfZJQAtnWWWgISy0jmtpFdH-7LjQwAB8M2Q9xSLEyBzhSkfsjsS2HnKe07Nf1m5K8nsa0AW-T35n_DA7w15GYbjk",
  "e": "AQAB",
  "kty": "RSA",
  "n": "0bArPvrqHxciV9Don9jB2mIcu6ZXpia76zpqZE3GnE_1lBW5X8OOEEwg3lhO7ggPjHkI3XYvBGCIWzv7cHJvTKUgY4O9v7RLTnAl0jqTItw93FM7d5cFoDXsQcu3Yss2xUPnhMC5QzK1f-k_HonOLDkiWv45EPKD-w8Iflk5rTJsgtWLtVia1bB859vua0r3JGijiWTzJdSuTROamzDnnDUIGh4AQdqul3zpxT9Yf6ZpeuZRkpSloAxoWcaFECwfAsbbVIYKGmgt82obEE3TFzBBM29ZYhGt141mN3YftGxjjrSB4iG6TPu5rI1DkFvYslZNtAoTT_aheowDiJbIwQ",
  "p": "7aaWylBd288K4A9LQDueVzEHaPTIAZC73ZVxKarYJL1M0hre2_CgTlYxTw3msCCc9js3mlwEc4xQgPA8bfpXnS3754j8OphoX4LvE2i-HkdUATvz_H5QekxhALDSwqvNVceHlckrAHpXRr2eIeSSRVo1PqtnoJn6re7i_xFrTGc",
  "q": "4eDe7c4I2MYrI4fX8DTvchMTmnDyHhxrF2CnuMC3fw9WhZdyiSJAJ_caEveKHjIgs4L3jrGhZBQF8VeLByfoipNXKg83o9kRdu-QPWuO40rEG4Jwb0haEiSMXWSw51rlt5sS_4Om4sGA-dqQT4SrDLKf-uvhko8yVu52jv7aiJc",
  "qi": "Q227Y9ybxw6L0ZO5xSH7zqTCJX2tMx-OgOtclULkSayalLHG9ZdazmJVa1jMn2Svf2v3Urdd4MKeh3bnQTvIQwux_QF9P9nVJqBj1t0wQ4JvpzJ-_8Z2aIKnkaMIGywzD9EYTRK7njwt-vdKHqmJAutviAILTiCY8mVPdRqJRYQ",
  "use": "sig"
}

headers = {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "df311e68-4bac-4457-b574-24e78be588ef"
}

payload = {
  "iss": "2006838577",
  "sub": "2006838577",
  "aud": "https://api.line.me/robofumo/",
  "exp":int(time.time())+(60 * 30),
  "token_exp": 60 * 60 * 24 * 30
}

key = RSAAlgorithm.from_jwk(privateKey)

JWT = jwt.encode(payload, key, algorithm="RS256", headers=headers, json_encoder=None)
print(JWT)

