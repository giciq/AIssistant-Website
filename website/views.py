from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import json
from website import answer
from bson import ObjectId
from datetime import datetime
from website import note_collection, user_collection

views = Blueprint('views', __name__)
def change(id):
    return ObjectId(id)
def to_string(id):
    return str(id)
@views.route('/mynotes', methods=['GET', 'POST'])
@login_required
def mynotes():
    if request.method == 'POST':
        if 'note' in request.form:
            question = request.form.get('note')

            if len(question) < 2:
                flash('Question seems to be too short!', category='error')
            else:
                response = answer(question)
                note = "User:\n" + question + "\nAssistant:\n" + response

                new_note = {
                    "data": note,
                    "date": datetime.utcnow(),
                    "user_id": current_user.id
                }
                note_collection.insert_one(new_note)
                flash('You got an answer!', category='success')
        elif 'edit_note' in request.form:
            note_id = request.form.get('note_id')
            edited_note_content = request.form.get('edit_note')

            if len(edited_note_content) < 2:
                flash('Edited question seems to be too short!', category='error')
            else:
                response = answer(edited_note_content)
                note_content = "User:\n" + edited_note_content + "\nAssistant:\n" + response
                note = note_collection.find_one({"_id": ObjectId(note_id)})
                if note and note['user_id'] == current_user.id:
                    note_collection.update_one(
                        {"_id": ObjectId(note_id)},
                        {"$set": {"data": note_content, "date": datetime.utcnow()}}
                    )
                    flash('Question updated', category='success')
                else:
                    flash('Question not found or unauthorized action', category='error')

    user_notes = note_collection.find({"user_id": current_user.id})
    return render_template("mynotes.html", user=current_user, notes=user_notes, str=to_string)

@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    user_notes = note_collection.find()
    return render_template("home.html", user=current_user, notes=user_notes,
                           username=current_user.first_name, user_collection=user_collection,
                           ObjectId=change)

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    data = json.loads(request.data)
    note_id = data['noteId']
    if not ObjectId.is_valid(note_id):
        return jsonify({'error': 'Invalid question ID'}), 400

    note = note_collection.find_one({"_id": ObjectId(note_id)})
    if note and note["user_id"] == current_user.id:
        note_collection.delete_one({"_id": ObjectId(note_id)})
        return jsonify({'success': 'Question deleted'}), 200

    return jsonify({'error': 'Question not found or not authorized'}), 404