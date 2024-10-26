from flask import Blueprint, make_response, request, jsonify
from bson import ObjectId
from decorators import jwt_required, admin_required
from globals import db

planets_bp = Blueprint("planets_bp", __name__)
bodies = db.bodies


@planets_bp.route("/api/v1.0/bodies/<string:s_id>/planets", methods=["GET"])
def query_all_planets(s_id):
    data_to_return = []
    body = bodies.find_one(
        {"_id": ObjectId(s_id)},
        {"planets": 1, "_id": 0})
    for planet in body["planets"]:
        planet["_id"] = str(planet["_id"])
        data_to_return.append(planet)
    return make_response(jsonify(data_to_return), 200)


@planets_bp.route("/api/v1.0/bodies/<string:s_id>/planets/<string:p_id>",
                  methods=["GET"])
def query_one_planet(s_id, p_id):
    body = bodies.find_one(
        {"planets._id": ObjectId(p_id)},
        {"_id": 0, "planets.$": 1})
    body["planets"][0]["_id"] = str(body["planets"][0]["_id"])
    if body is not None:
        return make_response(jsonify(body["planets"][0]), 200)
    else:
        return make_response(jsonify({"error": "invalid planet ID"}))


@planets_bp.route("/api/v1.0/bodies/<string:s_id>/planets", methods=["POST"])
@jwt_required
def add_planet(s_id):
    required_fields = ["name", "radius", "mass", "density",
                       "surface_temperature", "apoapsis",
                       "periapsis", "eccentricity",
                       "orbital_period", "status", "num_moons",
                       "contributed_by"]
    missing_fields = [field for field in required_fields
                      if not request.form.get(field)]
    if missing_fields:
        return make_response(jsonify(
            {"error": f"missing fields: {",".join(missing_fields)}"}), 404)
    planet_to_add = {
        "_id": ObjectId(),
        "name": request.form["name"],
        "radius": request.form["radius"],
        "mass": request.form["mass"],
        "density": request.form["density"],
        "surface_temperature": request.form["surface_temperature"],
        "apoapsis": request.form["apoapsis"],
        "periapsis": request.form["periapsis"],
        "eccentricity": request.form["eccentricity"],
        "orbital_period": request.form["orbital_period"],
        "status": request.form["status"],
        "num_moons": request.form["num_moons"],
        "contributed_by": request.form["contributed_by"]
    }
    bodies.update_one({"_id": ObjectId(s_id)}, {"$push":
                                                {"planets": planet_to_add}})
    new_planet_link = "http://127.0.0.1:5000/api/v1.0/bodies/" + \
        s_id + "/planets/" + str(planet_to_add["_id"])
    return make_response(jsonify({"url": new_planet_link}), 201)


@planets_bp.route("/api/v1.0/bodies/<string:s_id>/planets/<string:p_id>",
                  methods=["PUT"])
@jwt_required
def modify_planet(s_id, p_id):
    required_fields = ["name", "radius", "mass", "density",
                       "surface_temperature", "apoapsis",
                       "periapsis", "eccentricity",
                       "orbital_period", "status", "num_moons",
                       "contributed_by"]
    missing_fields = [field for field in required_fields
                      if not request.form.get(field)]
    if missing_fields:
        return make_response(jsonify(
            {"error": f"missing fields: {",".join(missing_fields)}"}), 404)
    modified_planet = {
        "planets.$.name": request.form["name"],
        "planets.$.radius": request.form["radius"],
        "planets.$.mass": request.form["mass"],
        "planets.$.density": request.form["density"],
        "planets.$.surface_temperature": request.form["surface_temperature"],
        "planets.$.apoapsis": request.form["apoapsis"],
        "planets.$.periapsis": request.form["periapsis"],
        "planets.$.eccentricity": request.form["eccentricity"],
        "planets.$.orbital_period": request.form["orbital_period"],
        "planets.$.status": request.form["status"],
        "planets.$.num_moons": request.form["num_moons"],
        "planets.$.contributed_by": request.form["contributed_by"]
    }
    result = bodies.update_one({"planets._id": ObjectId(p_id)},
                               {"$set": modified_planet})
    if result.matched_count == 1:
        modified_planet_url = "http://127.0.0.1:5000/api/v1.0/bodies/" + \
            s_id + "/planets/" + p_id
        return make_response(jsonify({"url": modified_planet_url}), 200)
    else:
        return make_response(jsonify({"error": "invalid planet ID"}), 404)


@planets_bp.route("/api/v1.0/bodies/<string:s_id>/planets/<string:p_id>",
                  methods=["DELETE"])
@jwt_required
@admin_required
def remove_planet(s_id, p_id):
    if ObjectId.is_valid(s_id):
        if ObjectId.is_valid(p_id):
            result = bodies.update_one({"_id": ObjectId(s_id)}, {
                            "$pull": {"planets": {"_id": ObjectId(p_id)}}})
            if result.matched_count == 1:
                return make_response(
                    jsonify({"message": "planet deleted successfully"}), 204)
            else:
                return make_response(
                    jsonify({"message": "deletion attempt failed"}), 500)
        else:
            return make_response(jsonify({"error": "invalid planet ID"}))
    else:
        return make_response(jsonify({"error": "invalid star ID"}))
