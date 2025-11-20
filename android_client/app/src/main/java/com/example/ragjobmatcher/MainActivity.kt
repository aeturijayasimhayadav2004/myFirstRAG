package com.example.ragjobmatcher

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Redirect to LoginActivity
        startActivity(Intent(this, LoginActivity::class.java))
        finish()
    }
}
