model.study().create("std1");
model.study("std1").create("eig", "Eigenfrequency");

model.study("std1").feature("eig").set("linpsolnum", "auto");
model.study("std1").feature("eig").set("solnum", "auto");
model.study("std1").feature("eig").set("notsolnum", "auto");
model.study("std1").feature("eig").set("outputmap", new String[]{});
model.study("std1").feature("eig").set("ngenAUX", "1");
model.study("std1").feature("eig").set("goalngenAUX", "1");
model.study("std1").feature("eig").set("ngenAUX", "1");
model.study("std1").feature("eig").set("goalngenAUX", "1");
model.study("std1").feature("eig").set("neigsactive", true);
model.study("std1").feature("eig").set("neigs", 3);
model.study("std1").feature("eig").set("eigwhich", "lr");

model.study("std1").create("param", "Parametric");


model.study("std1").feature("param").setIndex("punit", "", 0);
model.study("std1").feature("param").setIndex("pname", "", 0);
model.study("std1").feature("param").setIndex("plistarr", "", 0);
model.study("std1").feature("param").setIndex("punit", "", 0);

model.param().set("l", "1");
model.study("std1").feature("param").setIndex("pname", "l", 0);
model.study("std1").feature("param").setIndex("plistarr", "range(0.1,0.2,0.3)", 0);

model.study("std1").createAutoSequences("all");

model.sol().create("sol2");
model.sol("sol2").study("std1");
model.sol("sol2").label("Parametric Solutions 1");
model.batch("p1").feature("so1").set("psol", "sol2");
model.batch("p1").run("compute")

model.result().create("pg1", "PlotGroup3D");
model.result("pg1").set("data", "dset2");
model.result("pg1").setIndex("looplevel", 1, 0);
model.result("pg1").setIndex("looplevel", 2, 1);
model.result("pg1").create("mslc1", "Multislice");
model.result("pg1").feature("mslc1").set("expr", new String[]{"emw.normE"});
model.result("pg1").set("showlegendsmaxmin", true);
model.result("pg1").feature("mslc1").set("colortable", "RainbowLight");
model.result("pg1").label("Electric Field (emw)");
model.result().evaluationGroup().create("eg1", "EvaluationGroup");

model.result().evaluationGroup("eg1").set("data", "dset2");
model.result().evaluationGroup("eg1").label("Eigenfrequencies (emw)");
model.result().evaluationGroup("eg1").set("data", "dset2");
model.result().evaluationGroup("eg1").create("gev1", "EvalGlobal");
model.result().evaluationGroup("eg1").feature("gev1").label("Eigenfrequencies (emw)");
model.result().evaluationGroup("eg1").feature("gev1").set("expr", new String[]{"emw.freq", "emw.Qfactor"});
model.result().evaluationGroup("eg1").feature("gev1").set("unit", new String[]{"GHz", "1"});
model.result().table().create("tbl1", "Table");
model.result().evaluationGroup("eg1").feature("gev1").set("table", "tbl1");
model.result().evaluationGroup("eg1").run();
model.result("pg1").run();


model.study("std1").createAutoSequences("all");
model.sol().create("sol2");
model.sol("sol2").study("std1");
model.sol("sol2").label("Parametric Solutions 1");
model.batch("p1").feature("so1").set("psol", "sol2");
model.batch("p1").run("compute");

model.result().create("pg1", "PlotGroup3D");
model.result("pg1").set("data", "dset2");
model.result("pg1").setIndex("looplevel", 1, 0);
model.result("pg1").setIndex("looplevel", 2, 1);
model.result("pg1").create("mslc1", "Multislice");
model.result("pg1").feature("mslc1").set("expr", new String[]{"emw.normE"});
model.result("pg1").set("showlegendsmaxmin", true);
model.result("pg1").feature("mslc1").set("colortable", "RainbowLight");
model.result("pg1").label("Electric Field (emw)");

model.result().evaluationGroup().create("eg1", "EvaluationGroup");
model.result().evaluationGroup("eg1").set("data", "dset2");
model.result().evaluationGroup("eg1").label("Eigenfrequencies (emw)");


model.result().evaluationGroup("eg1").set("data", "dset2");
model.result().evaluationGroup("eg1").create("gev1", "EvalGlobal");

model.result().evaluationGroup("eg1").feature("gev1").label("Eigenfrequencies (emw)");
model.result().evaluationGroup("eg1").feature("gev1").set("expr", new String[]{"emw.freq", "emw.Qfactor"});
model.result().evaluationGroup("eg1").feature("gev1").set("unit", new String[]{"GHz", "1"});
model.result().table().create("tbl1", "Table");
model.result().evaluationGroup("eg1").feature("gev1").set("table", "tbl1");
model.result().evaluationGroup("eg1").run();
model.result("pg1").run();
