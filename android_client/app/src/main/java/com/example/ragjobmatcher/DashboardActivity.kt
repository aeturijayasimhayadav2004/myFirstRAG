package com.example.ragjobmatcher

import android.os.Bundle
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.ragjobmatcher.api.RetrofitClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class DashboardActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        val token = intent.getStringExtra("ACCESS_TOKEN")
        if (token != null) {
            fetchDashboard(token)
        } else {
            Toast.makeText(this, "Token missing", Toast.LENGTH_SHORT).show()
            finish()
        }
    }

    private fun fetchDashboard(token: String) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = RetrofitClient.instance.getDashboard("Bearer $token")
                withContext(Dispatchers.Main) {
                    if (response.isSuccessful && response.body() != null) {
                        val stats = response.body()!!
                        findViewById<TextView>(R.id.tvWelcome).text = "Welcome, ${stats.user_email}"
                        findViewById<TextView>(R.id.tvMatches).text = "Job Matches: ${stats.matches}"
                        findViewById<TextView>(R.id.tvApplications).text = "Applications Today: ${stats.applications_today}"
                        findViewById<TextView>(R.id.tvResumeStatus).text = "Resume Uploaded: ${if (stats.resume_uploaded) "Yes" else "No"}"
                    } else {
                        Toast.makeText(this@DashboardActivity, "Failed to load dashboard", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@DashboardActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
