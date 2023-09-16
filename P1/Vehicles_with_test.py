from Vehicles import Vehicle_detector
vehicle_detector = Vehicle_detector()
f = open("input.txt","r",encoding= "utf-8")
final = ""
for index,line in enumerate(f.readlines()):
    if index == 35:
        print(index)
    else:
        print(index)
    res = vehicle_detector.run(line.strip())
    for a in res:
        s = {
            "index":index,
            "input str" : line.strip(),
            "result" : a,
            "detected_vehicle":a["vehicle"],
            "v_span":a["vehicle_span"],
            "tested_V_span":line[a["vehicle_span"][0]:a["vehicle_span"][1]],
            "detected_from":a["from"],
            "s_span":a["from_span"],
            "tested_S_span":line[a["from_span"][0]:a["from_span"][1]],
            "detected_to":a["to"],
            "d_span":a["to_span"],
            "tested_D_span":line[a["to_span"][0]:a["to_span"][1]],
        }
        final+="\n".join([f"{str(key)} : {s[key]}" for key in s])+"\n"
    final+="\n\n"
f.close()
f = open("res.txt","w",encoding="utf-8")
f.write(final)
f.close()
