package com.example.ragjobmatcher.api

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {
    // REPLACE THIS WITH YOUR DEPLOYED URL (e.g., "https://my-rag-app.onrender.com/")
    // For local emulator testing, use "http://10.0.2.2:8000/"
    private const val BASE_URL = "http://10.0.2.2:8000/"

    val instance: ApiService by lazy {
        val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        retrofit.create(ApiService::class.java)
    }
}
