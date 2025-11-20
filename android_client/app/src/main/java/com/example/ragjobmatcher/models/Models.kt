package com.example.ragjobmatcher.models

data class LoginRequest(
    val username: String,
    val password: String
)

data class TokenResponse(
    val access_token: String,
    val token_type: String
)

data class DashboardStats(
    val matches: Int,
    val applications_today: Int,
    val resume_uploaded: Boolean,
    val user_email: String
)
