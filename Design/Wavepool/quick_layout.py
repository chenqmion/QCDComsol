model.geom("geom1").feature("wp2").geom().create("c_bulb_1", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("c_bulb_1").set("size", [h_bulb_1, w_bulb_1])
model.geom("geom1").feature("wp2").geom().feature("c_bulb_1").set("pos", [z_tube-h_bulb_1/2, x_bulb_1])

model.geom("geom1").feature("wp2").geom().create("w_bulb_1", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("w_bulb_1").set("size", [h_link_1, w_link_1])
model.geom("geom1").feature("wp2").geom().feature("w_bulb_1").set("pos", [z_tube-h_link_1/2, x_bulb_1+w_bulb_1])

model.geom("geom1").feature("wp2").geom().create("r_cap1", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("r_cap1").set("size", [h_cap_1, w_cap_1])
model.geom("geom1").feature("wp2").geom().feature("r_cap1").set("pos", [z_tube-h_cap_1/2, x_bulb_1+w_bulb_1+w_link_1])

model.geom("geom1").feature("wp2").geom().create("r_junction", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("r_junction").set("size", [h_junction, w_junction])
model.geom("geom1").feature("wp2").geom().feature("r_junction").set("pos", [z_tube-h_junction/2, x_bulb_1+w_bulb_1+w_link_1+w_cap_1])

model.geom("geom1").feature("wp2").geom().create("r_cap2", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("r_cap2").set("size", [h_cap_2, w_cap_2])
model.geom("geom1").feature("wp2").geom().feature("r_cap2").set("pos", [z_tube-h_cap_2/2, x_bulb_1+w_bulb_1+w_link_1+w_cap_1+w_junction])

model.geom("geom1").feature("wp2").geom().create("r_bulb_2", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("r_bulb_2").set("size", [h_bulb_2, w_link_2])
model.geom("geom1").feature("wp2").geom().feature("r_bulb_2").set("pos", [z_tube-h_bulb_2/2, x_bulb_2-w_link_2])

# model.geom("geom1").feature("wp2").geom().create("c_bulb_2", "Circle")
# model.geom("geom1").feature("wp2").geom().feature("c_bulb_2").set("r", r_bulb_2)
# model.geom("geom1").feature("wp2").geom().feature("c_bulb_2").set("pos", [x_bulb_2, 0])

model.geom("geom1").feature("wp2").geom().create("uni1", "Union")
model.geom("geom1").feature("wp2").geom().feature("uni1").selection("input").set("c_bulb_1", "w_bulb_1", "r_cap1")
model.geom("geom1").feature("wp2").geom().feature("uni1").set("intbnd", False)

model.geom("geom1").feature("wp2").geom().create("uni2", "Union")
model.geom("geom1").feature("wp2").geom().feature("uni2").selection("input").set("r_bulb_2", "r_cap2")
model.geom("geom1").feature("wp2").geom().feature("uni2").set("intbnd", False)

## resonator
model.geom("geom1").feature("wp2").geom().create("r1", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("r1").set("size", [w_resonator, l_resonator])
model.geom("geom1").feature("wp2").geom().feature("r1").set("pos", [z_tube-w_resonator/2, x_resonator])