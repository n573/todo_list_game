package com.island.todoquest.data

import android.content.Context
import com.google.gson.GsonBuilder
import java.io.File

class TaskRepository(private val context: Context) {
    private val gson = GsonBuilder().setPrettyPrinting().create()

    fun load(): TodoState {
        val file = dataFile()
        if (!file.exists()) {
            return TodoState()
        }
        return try {
            val json = file.readText()
            gson.fromJson(json, TodoState::class.java) ?: TodoState()
        } catch (_ex: Exception) {
            TodoState()
        }
    }

    fun save(state: TodoState) {
        val file = dataFile()
        val json = gson.toJson(state)
        file.writeText(json)
    }

    private fun dataFile(): File {
        return File(context.filesDir, "todo_data.json")
    }
}
