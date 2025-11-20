package com.example.ragjobmatcher.api

import com.example.ragjobmatcher.models.DashboardStats
import com.example.ragjobmatcher.models.LoginRequest
import com.example.ragjobmatcher.models.TokenResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST

interface ApiService {
    @FormUrlEncoded
    @POST("login")
    suspend fun login(
        @Field("username") username: String,
        @Field("password") password: String
    ): Response<TokenResponse>

    @GET("api/dashboard")
    suspend fun getDashboard(
        @Header("Authorization") token: String
    ): Response<DashboardStats>
}
