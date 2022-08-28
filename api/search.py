from flask import Flask, jsonify, redirect, render_template, request, session

def formatRow(row):
  return {
    "author_id": row['author_id'],
    "title": row['title'],
    "topic_id": row['topic_id'],
  }

def initializeSearchApiRoute(app, db):
  @app.route("/api/search/<string:query>")
  def search(query):
    queryResult = db.execute("SELECT title, author_id, topic_id FROM topics WHERE title LIKE ? LIMIT 10", (f'%{query}%'))
    return jsonify({
      "results": list(map(formatRow, queryResult))
    })