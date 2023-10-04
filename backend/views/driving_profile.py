import os
import pymongo

client = pymongo.MongoClient(os.environ["SPEEDCOP_DATABASE"])

database = client.sihdatabase


def update_driving_profile(vehicle_no, speed, left_sum, right_sum, l_count, r_count):
    if speed > 20:
        try:
            vehicle = database.vehicles.find_one({"vehicle_no": vehicle_no})
            if vehicle:
                avg_left = vehicle['avg_left']
                avg_right = vehicle['avg_right']
                left_count = vehicle['left_count']
                right_count = vehicle['right_count']

                n1 = left_count + l_count
                n2 = right_count + r_count
                total_left = (left_count * avg_left + left_sum) / n1
                total_right = (left_count * avg_right + right_sum) / n2

                database.vehicles.update({"vehicle_no": vehicle_no},
                                         {"$set": {"avg_left": total_left, "avg_right": total_right, "left_count": n1,
                                                   "right_count": n2}})

        except pymongo.errors.OperationFailure as e:
            print(e)
