<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:afaf73eb-94a1-4aae-902b-ed4d28124667(jetbrains.mps.samples.componentDependencies.structure)">
  <persistence version="9" />
  <languages>
    <devkit ref="78434eb8-b0e5-444b-850d-e7c4ad2da9ab(jetbrains.mps.devkit.aspect.structure)" />
  </languages>
  <imports>
    <import index="tpck" ref="r:00000000-0000-4000-0000-011c89590288(jetbrains.mps.lang.core.structure)" implicit="true" />
  </imports>
  <registry>
    <language id="c72da2b9-7cce-4447-8389-f407dc1158b7" name="jetbrains.mps.lang.structure">
      <concept id="1169125787135" name="jetbrains.mps.lang.structure.structure.AbstractConceptDeclaration" flags="ig" index="PkWjJ">
        <property id="6714410169261853888" name="conceptId" index="EcuMT" />
        <property id="5092175715804935370" name="conceptAlias" index="34LRSv" />
        <child id="1071489727083" name="linkDeclaration" index="1TKVEi" />
        <child id="1071489727084" name="propertyDeclaration" index="1TKVEl" />
      </concept>
      <concept id="1169127622168" name="jetbrains.mps.lang.structure.structure.InterfaceConceptReference" flags="ig" index="PrWs8">
        <reference id="1169127628841" name="intfc" index="PrY4T" />
      </concept>
      <concept id="1071489090640" name="jetbrains.mps.lang.structure.structure.ConceptDeclaration" flags="ig" index="1TIwiD">
        <property id="1096454100552" name="rootable" index="19KtqR" />
        <reference id="1071489389519" name="extends" index="1TJDcQ" />
        <child id="1169129564478" name="implements" index="PzmwI" />
      </concept>
      <concept id="1071489288299" name="jetbrains.mps.lang.structure.structure.PropertyDeclaration" flags="ig" index="1TJgyi">
        <property id="241647608299431129" name="propertyId" index="IQ2nx" />
        <reference id="1082985295845" name="dataType" index="AX2Wp" />
      </concept>
      <concept id="1071489288298" name="jetbrains.mps.lang.structure.structure.LinkDeclaration" flags="ig" index="1TJgyj">
        <property id="1071599776563" name="role" index="20kJfa" />
        <property id="1071599893252" name="sourceCardinality" index="20lbJX" />
        <property id="1071599937831" name="metaClass" index="20lmBu" />
        <property id="241647608299431140" name="linkId" index="IQ2ns" />
        <reference id="1071599976176" name="target" index="20lvS9" />
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1133920641626" name="jetbrains.mps.lang.core.structure.BaseConcept" flags="ng" index="2VYdi">
        <property id="1193676396447" name="virtualPackage" index="3GE5qa" />
      </concept>
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ngI" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
  </registry>
  <node concept="1TIwiD" id="5pu6noS52gF">
    <property role="TrG5h" value="ComponentSet" />
    <property role="19KtqR" value="true" />
    <property role="EcuMT" value="6223439730610283563" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="6sC7QXwR9qu" role="1TKVEl">
      <property role="TrG5h" value="query" />
      <property role="IQ2nx" value="7433225748201903774" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="5pu6noS56YC" role="1TKVEi">
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20kJfa" value="component" />
      <property role="20lbJX" value="fLJekj6/1..n" />
      <property role="IQ2ns" value="6223439730610302888" />
      <ref role="20lvS9" node="5pu6noS5f54" resolve="Component" />
    </node>
    <node concept="PrWs8" id="5pu6noS5f52" role="PzmwI">
      <ref role="PrY4T" to="tpck:h0TrEE$" resolve="INamedConcept" />
    </node>
  </node>
  <node concept="1TIwiD" id="5pu6noS5f54">
    <property role="TrG5h" value="Component" />
    <property role="EcuMT" value="6223439730610336068" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="5pu6noS6XHd" role="1TKVEl">
      <property role="TrG5h" value="x" />
      <property role="IQ2nx" value="6223439730610789197" />
      <ref role="AX2Wp" to="tpck:fKAQMTA" resolve="integer" />
    </node>
    <node concept="1TJgyi" id="5pu6noS6XHf" role="1TKVEl">
      <property role="TrG5h" value="y" />
      <property role="IQ2nx" value="6223439730610789199" />
      <ref role="AX2Wp" to="tpck:fKAQMTA" resolve="integer" />
    </node>
    <node concept="1TJgyi" id="74C6il$sxI8" role="1TKVEl">
      <property role="TrG5h" value="width" />
      <property role="IQ2nx" value="8153794773743967112" />
      <ref role="AX2Wp" to="tpck:fKAQMTA" resolve="integer" />
    </node>
    <node concept="1TJgyi" id="74C6il$sxIf" role="1TKVEl">
      <property role="TrG5h" value="heigh" />
      <property role="IQ2nx" value="8153794773743967119" />
      <ref role="AX2Wp" to="tpck:fKAQMTA" resolve="integer" />
    </node>
    <node concept="1TJgyi" id="74C6il$sxIF" role="1TKVEl">
      <property role="TrG5h" value="subsystem" />
      <property role="IQ2nx" value="8153794773743967147" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="5pu6noS5f57" role="1TKVEi">
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20kJfa" value="dep" />
      <property role="20lbJX" value="fLJekj5/0..n" />
      <property role="IQ2ns" value="6223439730610336071" />
      <ref role="20lvS9" node="5pu6noS6R6w" resolve="Dependency" />
    </node>
    <node concept="1TJgyj" id="5pu6noS6Y52" role="1TKVEi">
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20kJfa" value="in" />
      <property role="20lbJX" value="fLJekj5/0..n" />
      <property role="IQ2ns" value="6223439730610790722" />
      <ref role="20lvS9" node="5pu6noS6Y5A" resolve="InPort" />
    </node>
    <node concept="1TJgyj" id="5pu6noS6Y56" role="1TKVEi">
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20kJfa" value="out" />
      <property role="20lbJX" value="fLJekj5/0..n" />
      <property role="IQ2ns" value="6223439730610790726" />
      <ref role="20lvS9" node="5pu6noS6Y55" resolve="OutPort" />
    </node>
    <node concept="PrWs8" id="5pu6noS5f55" role="PzmwI">
      <ref role="PrY4T" to="tpck:h0TrEE$" resolve="INamedConcept" />
    </node>
  </node>
  <node concept="1TIwiD" id="5pu6noS6R6w">
    <property role="TrG5h" value="Dependency" />
    <property role="34LRSv" value="depends on" />
    <property role="EcuMT" value="6223439730610762144" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyj" id="5pu6noS6Rpk" role="1TKVEi">
      <property role="20kJfa" value="to" />
      <property role="20lbJX" value="fLJekj4/1" />
      <property role="IQ2ns" value="6223439730610763348" />
      <ref role="20lvS9" node="5pu6noS5f54" resolve="Component" />
    </node>
  </node>
  <node concept="1TIwiD" id="5pu6noS6Y55">
    <property role="TrG5h" value="OutPort" />
    <property role="3GE5qa" value="" />
    <property role="EcuMT" value="6223439730610790725" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="PrWs8" id="74C6il$gx0s" role="PzmwI">
      <ref role="PrY4T" to="tpck:h0TrEE$" resolve="INamedConcept" />
    </node>
  </node>
  <node concept="1TIwiD" id="5pu6noS6Y5A">
    <property role="TrG5h" value="InPort" />
    <property role="3GE5qa" value="" />
    <property role="EcuMT" value="6223439730610790758" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="PrWs8" id="74C6il$gx0a" role="PzmwI">
      <ref role="PrY4T" to="tpck:h0TrEE$" resolve="INamedConcept" />
    </node>
  </node>
</model>

