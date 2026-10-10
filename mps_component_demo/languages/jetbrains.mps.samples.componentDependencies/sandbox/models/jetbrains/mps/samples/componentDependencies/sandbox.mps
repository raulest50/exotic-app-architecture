<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:436384fb-e97b-487f-9379-826737776648(cg.demo.stateMachine.sandbox)">
  <persistence version="9" />
  <languages>
    <use id="3066bc09-2438-4300-a936-5bd59917ae9b" name="jetbrains.mps.samples.componentDependencies" version="0" />
    <use id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core" version="2" />
    <use id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage" version="12" />
  </languages>
  <imports />
  <registry>
    <language id="3066bc09-2438-4300-a936-5bd59917ae9b" name="jetbrains.mps.samples.componentDependencies">
      <concept id="6223439730610762144" name="jetbrains.mps.samples.componentDependencies.structure.Dependency" flags="ng" index="1Ihmzm">
        <reference id="6223439730610763348" name="to" index="1IhmWy" />
      </concept>
      <concept id="6223439730610790758" name="jetbrains.mps.samples.componentDependencies.structure.InPort" flags="ng" index="1Ihvwg" />
      <concept id="6223439730610790725" name="jetbrains.mps.samples.componentDependencies.structure.OutPort" flags="ng" index="1IhvwN" />
      <concept id="6223439730610283563" name="jetbrains.mps.samples.componentDependencies.structure.ComponentSet" flags="ng" index="1IizPt">
        <child id="6223439730610302888" name="component" index="1IiBru" />
      </concept>
      <concept id="6223439730610336068" name="jetbrains.mps.samples.componentDependencies.structure.Component" flags="ng" index="1IiIwM">
        <property id="8153794773743967147" name="subsystem" index="lmwae" />
        <property id="8153794773743967119" name="heigh" index="lmwaE" />
        <property id="8153794773743967112" name="width" index="lmwaH" />
        <property id="6223439730610789199" name="y" index="1Ihs8T" />
        <property id="6223439730610789197" name="x" index="1Ihs8V" />
        <child id="6223439730610790726" name="out" index="1IhvwK" />
        <child id="6223439730610790722" name="in" index="1IhvwO" />
        <child id="6223439730610336071" name="dep" index="1IiIwL" />
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ngI" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
  </registry>
  <node concept="1IizPt" id="3ydhewaw6ZH">
    <property role="TrG5h" value="MPSComponents" />
    <node concept="1IiIwM" id="3ydhewaw724" role="1IiBru">
      <property role="1Ihs8V" value="10" />
      <property role="1Ihs8T" value="10" />
      <property role="TrG5h" value="openapi" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="100" />
      <property role="lmwae" value="&lt;&lt;API&gt;&gt;" />
      <node concept="1Ihvwg" id="74C6il$gOy$" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
      <node concept="1Ihvwg" id="3ydhewaw725" role="1IhvwO">
        <property role="TrG5h" value="smodel" />
      </node>
    </node>
    <node concept="1IiIwM" id="3ydhewaw715" role="1IiBru">
      <property role="1Ihs8V" value="150" />
      <property role="1Ihs8T" value="10" />
      <property role="TrG5h" value="Tuples-runtime" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="150" />
      <property role="lmwae" value="&lt;&lt;runtime&gt;&gt;" />
      <node concept="1Ihvwg" id="3ydhewaw716" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
    </node>
    <node concept="1IiIwM" id="3ydhewaw76l" role="1IiBru">
      <property role="1Ihs8V" value="350" />
      <property role="1Ihs8T" value="10" />
      <property role="TrG5h" value="Closures-runtime" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="150" />
      <property role="lmwae" value="&lt;&lt;runtime&gt;&gt;" />
      <node concept="1Ihvwg" id="3ydhewaw76m" role="1IhvwO">
        <property role="TrG5h" value="collections-runtime" />
      </node>
      <node concept="1Ihvwg" id="74C6il$gQ41" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
    </node>
    <node concept="1IiIwM" id="3ydhewaw71k" role="1IiBru">
      <property role="1Ihs8V" value="10" />
      <property role="1Ihs8T" value="150" />
      <property role="TrG5h" value="smodel" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="100" />
      <property role="lmwae" value="&lt;&lt;module&gt;&gt;" />
      <node concept="1Ihmzm" id="3ydhewaw73f" role="1IiIwL">
        <ref role="1IhmWy" node="3ydhewaw724" resolve="openapi" />
      </node>
      <node concept="1Ihvwg" id="3ydhewaw71l" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
      <node concept="1IhvwN" id="3ydhewaw71m" role="1IhvwK">
        <property role="TrG5h" value="openapi" />
      </node>
    </node>
    <node concept="1IiIwM" id="3ydhewaw77k" role="1IiBru">
      <property role="1Ihs8V" value="300" />
      <property role="1Ihs8T" value="150" />
      <property role="TrG5h" value="collections-runtime" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="200" />
      <property role="lmwae" value="&lt;&lt;runtime&gt;&gt;" />
      <node concept="1Ihmzm" id="3cyPm1rutHm" role="1IiIwL">
        <ref role="1IhmWy" node="3ydhewaw76l" resolve="Closures-runtime" />
      </node>
      <node concept="1Ihvwg" id="74C6il$gQ9E" role="1IhvwO">
        <property role="TrG5h" value="typesystemEngine" />
      </node>
      <node concept="1Ihvwg" id="3ydhewaw77l" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
      <node concept="1IhvwN" id="3ydhewaw77m" role="1IhvwK">
        <property role="TrG5h" value="Closures-runtime" />
      </node>
    </node>
    <node concept="1IiIwM" id="3ydhewaw7b1" role="1IiBru">
      <property role="1Ihs8V" value="164" />
      <property role="1Ihs8T" value="369" />
      <property role="TrG5h" value="kernel" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="150" />
      <property role="lmwae" value="&lt;&lt;module&gt;&gt;" />
      <node concept="1Ihmzm" id="3ydhewaw7c$" role="1IiIwL">
        <ref role="1IhmWy" node="3ydhewaw724" resolve="openapi" />
      </node>
      <node concept="1Ihmzm" id="3ydhewaw7cB" role="1IiIwL">
        <ref role="1IhmWy" node="3ydhewaw71k" resolve="smodel" />
      </node>
      <node concept="1Ihmzm" id="3ydhewaw7e6" role="1IiIwL">
        <ref role="1IhmWy" node="3ydhewaw715" resolve="Tuples-runtime" />
      </node>
      <node concept="1Ihmzm" id="3ydhewaw7f5" role="1IiIwL">
        <ref role="1IhmWy" node="3ydhewaw77k" resolve="collections-runtime" />
      </node>
      <node concept="1Ihmzm" id="3cyPm1rutHo" role="1IiIwL">
        <ref role="1IhmWy" node="3ydhewaw76l" resolve="Closures-runtime" />
      </node>
      <node concept="1Ihmzm" id="3ydhewaw7g0" role="1IiIwL">
        <ref role="1IhmWy" node="3ydhewaw796" resolve="typesystemEngine" />
      </node>
      <node concept="1IhvwN" id="74C6il$gQ8M" role="1IhvwK">
        <property role="TrG5h" value="smodel" />
      </node>
      <node concept="1IhvwN" id="3ydhewaw7b3" role="1IhvwK">
        <property role="TrG5h" value="openapi" />
      </node>
      <node concept="1IhvwN" id="74C6il$gQ6k" role="1IhvwK">
        <property role="TrG5h" value="Tuples-runtime" />
      </node>
      <node concept="1IhvwN" id="74C6il$gQ7a" role="1IhvwK">
        <property role="TrG5h" value="Closures-runtime" />
      </node>
      <node concept="1IhvwN" id="74C6il$gQ9H" role="1IhvwK">
        <property role="TrG5h" value="collections-runtime" />
      </node>
      <node concept="1IhvwN" id="74C6il$gQbx" role="1IhvwK">
        <property role="TrG5h" value="typesystemEngine" />
      </node>
    </node>
    <node concept="1IiIwM" id="3ydhewaw796" role="1IiBru">
      <property role="1Ihs8V" value="420" />
      <property role="1Ihs8T" value="299" />
      <property role="TrG5h" value="typesystemEngine" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="150" />
      <property role="lmwae" value="&lt;&lt;module&gt;&gt;" />
      <node concept="1Ihmzm" id="3ydhewaw7an" role="1IiIwL">
        <ref role="1IhmWy" node="3ydhewaw77k" resolve="collections-runtime" />
      </node>
      <node concept="1Ihvwg" id="3ydhewaw797" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
      <node concept="1IhvwN" id="3ydhewaw798" role="1IhvwK">
        <property role="TrG5h" value="collections-runtime" />
      </node>
    </node>
  </node>
  <node concept="1IizPt" id="3cyPm1rutH_">
    <property role="TrG5h" value="MPSComponentsWithErrors" />
    <node concept="1IiIwM" id="3cyPm1rutHA" role="1IiBru">
      <property role="1Ihs8V" value="10" />
      <property role="1Ihs8T" value="10" />
      <property role="TrG5h" value="openapi" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="100" />
      <property role="lmwae" value="&lt;&lt;API&gt;&gt;" />
      <node concept="1Ihvwg" id="3cyPm1rutHB" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
      <node concept="1Ihvwg" id="3cyPm1rutHC" role="1IhvwO">
        <property role="TrG5h" value="smodel" />
      </node>
    </node>
    <node concept="1IiIwM" id="3cyPm1rutHD" role="1IiBru">
      <property role="1Ihs8V" value="150" />
      <property role="1Ihs8T" value="10" />
      <property role="TrG5h" value="Tuples-runtime" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="150" />
      <property role="lmwae" value="&lt;&lt;runtime&gt;&gt;" />
      <node concept="1Ihvwg" id="3cyPm1rutHE" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
    </node>
    <node concept="1IiIwM" id="3cyPm1rutHF" role="1IiBru">
      <property role="1Ihs8V" value="350" />
      <property role="1Ihs8T" value="10" />
      <property role="TrG5h" value="Closures-runtime" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="150" />
      <property role="lmwae" value="&lt;&lt;runtime&gt;&gt;" />
      <node concept="1Ihvwg" id="3cyPm1rutHG" role="1IhvwO">
        <property role="TrG5h" value="collections-runtime" />
      </node>
      <node concept="1Ihvwg" id="3cyPm1rutHH" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
    </node>
    <node concept="1IiIwM" id="3cyPm1rutHI" role="1IiBru">
      <property role="1Ihs8V" value="10" />
      <property role="1Ihs8T" value="150" />
      <property role="TrG5h" value="smodel" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="100" />
      <property role="lmwae" value="&lt;&lt;module&gt;&gt;" />
      <node concept="1Ihmzm" id="3cyPm1rutHJ" role="1IiIwL">
        <ref role="1IhmWy" node="3cyPm1rutHA" resolve="openapi" />
      </node>
      <node concept="1Ihvwg" id="3cyPm1rutHK" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
      <node concept="1IhvwN" id="3cyPm1rutHL" role="1IhvwK">
        <property role="TrG5h" value="openapi" />
      </node>
    </node>
    <node concept="1IiIwM" id="3cyPm1rutHM" role="1IiBru">
      <property role="1Ihs8V" value="300" />
      <property role="1Ihs8T" value="150" />
      <property role="TrG5h" value="collections-runtime" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="200" />
      <property role="lmwae" value="&lt;&lt;runtime&gt;&gt;" />
      <node concept="1Ihmzm" id="3cyPm1rutHN" role="1IiIwL">
        <ref role="1IhmWy" node="3cyPm1rutHF" resolve="Closures-runtime" />
      </node>
      <node concept="1Ihvwg" id="3cyPm1rutHO" role="1IhvwO">
        <property role="TrG5h" value="typesystemEngine" />
      </node>
      <node concept="1Ihvwg" id="3cyPm1rutHP" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
      <node concept="1IhvwN" id="3cyPm1rutHQ" role="1IhvwK">
        <property role="TrG5h" value="Closures-runtime" />
      </node>
    </node>
    <node concept="1IiIwM" id="3cyPm1rutHR" role="1IiBru">
      <property role="1Ihs8V" value="164" />
      <property role="1Ihs8T" value="369" />
      <property role="TrG5h" value="kernel" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="150" />
      <property role="lmwae" value="&lt;&lt;module&gt;&gt;" />
      <node concept="1Ihmzm" id="3cyPm1rutHS" role="1IiIwL">
        <ref role="1IhmWy" node="3cyPm1rutHA" resolve="openapi" />
      </node>
      <node concept="1Ihmzm" id="3cyPm1rutHT" role="1IiIwL">
        <ref role="1IhmWy" node="3cyPm1rutHI" resolve="smodel" />
      </node>
      <node concept="1Ihmzm" id="3cyPm1rutHU" role="1IiIwL">
        <ref role="1IhmWy" node="3cyPm1rutHD" resolve="Tuples-runtime" />
      </node>
      <node concept="1Ihmzm" id="3cyPm1rutHV" role="1IiIwL">
        <ref role="1IhmWy" node="3cyPm1rutHM" resolve="collections-runtime" />
      </node>
      <node concept="1Ihmzm" id="3cyPm1rutHW" role="1IiIwL">
        <ref role="1IhmWy" node="3cyPm1rutHF" resolve="Closures-runtime" />
      </node>
      <node concept="1Ihmzm" id="3cyPm1rutHX" role="1IiIwL">
        <ref role="1IhmWy" node="3cyPm1rutI5" resolve="typesystemEngine" />
      </node>
      <node concept="1Ihvwg" id="3cyPm1rutHY" role="1IhvwO">
        <property role="TrG5h" value="typesystemEngine" />
      </node>
      <node concept="1IhvwN" id="3cyPm1rutHZ" role="1IhvwK">
        <property role="TrG5h" value="smodel" />
      </node>
      <node concept="1IhvwN" id="3cyPm1rutI0" role="1IhvwK">
        <property role="TrG5h" value="openapi" />
      </node>
      <node concept="1IhvwN" id="3cyPm1rutI1" role="1IhvwK">
        <property role="TrG5h" value="Tuples-runtime" />
      </node>
      <node concept="1IhvwN" id="3cyPm1rutI2" role="1IhvwK">
        <property role="TrG5h" value="Closures-runtime" />
      </node>
      <node concept="1IhvwN" id="3cyPm1rutI3" role="1IhvwK">
        <property role="TrG5h" value="collections-runtime" />
      </node>
      <node concept="1IhvwN" id="3cyPm1rutI4" role="1IhvwK">
        <property role="TrG5h" value="typesystemEngine" />
      </node>
    </node>
    <node concept="1IiIwM" id="3cyPm1rutI5" role="1IiBru">
      <property role="1Ihs8V" value="420" />
      <property role="1Ihs8T" value="300" />
      <property role="TrG5h" value="typesystemEngine" />
      <property role="lmwaE" value="60" />
      <property role="lmwaH" value="150" />
      <property role="lmwae" value="&lt;&lt;module&gt;&gt;" />
      <node concept="1Ihmzm" id="3cyPm1rutI6" role="1IiIwL">
        <ref role="1IhmWy" node="3cyPm1rutHM" resolve="collections-runtime" />
      </node>
      <node concept="1Ihmzm" id="3cyPm1rutI7" role="1IiIwL">
        <ref role="1IhmWy" node="3cyPm1rutHR" resolve="kernel" />
      </node>
      <node concept="1Ihvwg" id="3cyPm1rutI8" role="1IhvwO">
        <property role="TrG5h" value="kernel" />
      </node>
      <node concept="1IhvwN" id="3cyPm1rutI9" role="1IhvwK">
        <property role="TrG5h" value="collections-runtime" />
      </node>
      <node concept="1IhvwN" id="3cyPm1rutIa" role="1IhvwK">
        <property role="TrG5h" value="kernel" />
      </node>
    </node>
  </node>
</model>

