<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:f6a83d73-3fb1-4112-81c5-3c468d09b36a(main@generator)">
  <persistence version="9" />
  <languages>
    <use id="3066bc09-2438-4300-a936-5bd59917ae9b" name="jetbrains.mps.samples.componentDependencies" version="0" />
    <use id="479c7a8c-02f9-43b5-9139-d910cb22f298" name="jetbrains.mps.core.xml" version="0" />
    <devkit ref="a2eb3a43-fcc2-4200-80dc-c60110c4862d(jetbrains.mps.devkit.templates)" />
  </languages>
  <imports>
    <import index="ktbj" ref="r:afaf73eb-94a1-4aae-902b-ed4d28124667(jetbrains.mps.samples.componentDependencies.structure)" />
    <import index="tpck" ref="r:00000000-0000-4000-0000-011c89590288(jetbrains.mps.lang.core.structure)" implicit="true" />
  </imports>
  <registry>
    <language id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage">
      <concept id="1197027756228" name="jetbrains.mps.baseLanguage.structure.DotExpression" flags="nn" index="2OqwBi">
        <child id="1197027771414" name="operand" index="2Oq$k0" />
        <child id="1197027833540" name="operation" index="2OqNvi" />
      </concept>
      <concept id="1137021947720" name="jetbrains.mps.baseLanguage.structure.ConceptFunction" flags="in" index="2VMwT0">
        <child id="1137022507850" name="body" index="2VODD2" />
      </concept>
      <concept id="1068580123155" name="jetbrains.mps.baseLanguage.structure.ExpressionStatement" flags="nn" index="3clFbF">
        <child id="1068580123156" name="expression" index="3clFbG" />
      </concept>
      <concept id="1068580123136" name="jetbrains.mps.baseLanguage.structure.StatementList" flags="sn" stub="5293379017992965193" index="3clFbS">
        <child id="1068581517665" name="statement" index="3cqZAp" />
      </concept>
    </language>
    <language id="479c7a8c-02f9-43b5-9139-d910cb22f298" name="jetbrains.mps.core.xml">
      <concept id="6666499814681515200" name="jetbrains.mps.core.xml.structure.XmlFile" flags="ng" index="2pMbU2">
        <child id="6666499814681515201" name="document" index="2pMbU3" />
      </concept>
      <concept id="6666499814681541919" name="jetbrains.mps.core.xml.structure.XmlTextValue" flags="ng" index="2pMdtt" />
      <concept id="6666499814681415858" name="jetbrains.mps.core.xml.structure.XmlElement" flags="ng" index="2pNNFK">
        <property id="6666499814681415862" name="tagName" index="2pNNFO" />
        <child id="6666499814681415861" name="attributes" index="2pNNFR" />
        <child id="1622293396948928802" name="content" index="3o6s8t" />
      </concept>
      <concept id="6666499814681447923" name="jetbrains.mps.core.xml.structure.XmlAttribute" flags="ng" index="2pNUuL">
        <property id="6666499814681447926" name="attrName" index="2pNUuO" />
        <child id="6666499814681541918" name="value" index="2pMdts" />
      </concept>
      <concept id="1622293396948952339" name="jetbrains.mps.core.xml.structure.XmlText" flags="nn" index="3o6iSG">
        <property id="1622293396948953704" name="value" index="3o6i5n" />
      </concept>
      <concept id="6786756355279841993" name="jetbrains.mps.core.xml.structure.XmlDocument" flags="ng" index="3rIKKV">
        <child id="6666499814681299055" name="rootElement" index="2pNm8H" />
      </concept>
    </language>
    <language id="b401a680-8325-4110-8fd3-84331ff25bef" name="jetbrains.mps.lang.generator">
      <concept id="1114729360583" name="jetbrains.mps.lang.generator.structure.CopySrcListMacro" flags="lg" index="2b32R4">
        <child id="1168278589236" name="sourceNodesQuery" index="2P8S$" />
      </concept>
      <concept id="1095416546421" name="jetbrains.mps.lang.generator.structure.MappingConfiguration" flags="ig" index="bUwia">
        <child id="1167328349397" name="reductionMappingRule" index="3acgRq" />
        <child id="1167514678247" name="rootMappingRule" index="3lj3bC" />
      </concept>
      <concept id="1168559333462" name="jetbrains.mps.lang.generator.structure.TemplateDeclarationReference" flags="ln" index="j$656" />
      <concept id="1168619357332" name="jetbrains.mps.lang.generator.structure.RootTemplateAnnotation" flags="lg" index="n94m4">
        <reference id="1168619429071" name="applicableConcept" index="n9lRv" />
      </concept>
      <concept id="1095672379244" name="jetbrains.mps.lang.generator.structure.TemplateFragment" flags="ng" index="raruj" />
      <concept id="1722980698497626400" name="jetbrains.mps.lang.generator.structure.ITemplateCall" flags="ngI" index="v9R3L">
        <reference id="1722980698497626483" name="template" index="v9R2y" />
      </concept>
      <concept id="1167169188348" name="jetbrains.mps.lang.generator.structure.TemplateFunctionParameter_sourceNode" flags="nn" index="30H73N" />
      <concept id="1167169308231" name="jetbrains.mps.lang.generator.structure.BaseMappingRule" flags="ng" index="30H$t8">
        <reference id="1167169349424" name="applicableConcept" index="30HIoZ" />
      </concept>
      <concept id="1092059087312" name="jetbrains.mps.lang.generator.structure.TemplateDeclaration" flags="ig" index="13MO4I">
        <reference id="1168285871518" name="applicableConcept" index="3gUMe" />
        <child id="1092060348987" name="contentNode" index="13RCb5" />
      </concept>
      <concept id="1087833241328" name="jetbrains.mps.lang.generator.structure.PropertyMacro" flags="lg" index="17Uvod">
        <child id="1167756362303" name="propertyValueFunction" index="3zH0cK" />
      </concept>
      <concept id="1167327847730" name="jetbrains.mps.lang.generator.structure.Reduction_MappingRule" flags="lg" index="3aamgX">
        <child id="1169672767469" name="ruleConsequence" index="1lVwrX" />
      </concept>
      <concept id="1167514355419" name="jetbrains.mps.lang.generator.structure.Root_MappingRule" flags="lg" index="3lhOvk">
        <reference id="1167514355421" name="template" index="3lhOvi" />
      </concept>
      <concept id="1167756080639" name="jetbrains.mps.lang.generator.structure.PropertyMacro_GetPropertyValue" flags="in" index="3zFVjK" />
      <concept id="1167951910403" name="jetbrains.mps.lang.generator.structure.SourceSubstituteMacro_SourceNodesQuery" flags="ig" index="3JmXsc" />
    </language>
    <language id="7866978e-a0f0-4cc7-81bc-4d213d9375e1" name="jetbrains.mps.lang.smodel">
      <concept id="1138056022639" name="jetbrains.mps.lang.smodel.structure.SPropertyAccess" flags="nn" index="3TrcHB">
        <reference id="1138056395725" name="property" index="3TsBF5" />
      </concept>
      <concept id="1138056143562" name="jetbrains.mps.lang.smodel.structure.SLinkAccess" flags="nn" index="3TrEf2">
        <reference id="1138056516764" name="link" index="3Tt5mk" />
      </concept>
      <concept id="1138056282393" name="jetbrains.mps.lang.smodel.structure.SLinkListAccess" flags="nn" index="3Tsc0h">
        <reference id="1138056546658" name="link" index="3TtcxE" />
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1133920641626" name="jetbrains.mps.lang.core.structure.BaseConcept" flags="ng" index="2VYdi">
        <child id="5169995583184591170" name="smodelAttribute" index="lGtFl" />
      </concept>
      <concept id="3364660638048049750" name="jetbrains.mps.lang.core.structure.PropertyAttribute" flags="ng" index="A9Btg">
        <property id="1757699476691236117" name="name_DebugInfo" index="2qtEX9" />
        <property id="1341860900487648621" name="propertyId" index="P4ACc" />
      </concept>
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ngI" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
  </registry>
  <node concept="bUwia" id="1KaxGo$aK88">
    <property role="TrG5h" value="main" />
    <node concept="3aamgX" id="1KaxGo$aQ8u" role="3acgRq">
      <ref role="30HIoZ" to="ktbj:5pu6noS5f54" resolve="Component" />
      <node concept="j$656" id="1KaxGo$aQ8y" role="1lVwrX">
        <ref role="v9R2y" node="1KaxGo$aQ8w" resolve="reduce_Component" />
      </node>
    </node>
    <node concept="3aamgX" id="1KaxGo$b44Z" role="3acgRq">
      <ref role="30HIoZ" to="ktbj:5pu6noS6R6w" resolve="Dependency" />
      <node concept="j$656" id="1KaxGo$b453" role="1lVwrX">
        <ref role="v9R2y" node="1KaxGo$b451" resolve="reduce_Dependency" />
      </node>
    </node>
    <node concept="3lhOvk" id="1KaxGo$aK89" role="3lj3bC">
      <ref role="30HIoZ" to="ktbj:5pu6noS52gF" resolve="ComponentSet" />
      <ref role="3lhOvi" node="1KaxGo$aK96" resolve="map_ComponentSet" />
    </node>
  </node>
  <node concept="2pMbU2" id="1KaxGo$aK96">
    <property role="TrG5h" value="map_ComponentSet" />
    <node concept="3rIKKV" id="1KaxGo$aK97" role="2pMbU3">
      <node concept="2pNNFK" id="1KaxGo$aKvj" role="2pNm8H">
        <property role="2pNNFO" value="components" />
        <node concept="2pNNFK" id="1KaxGo$cGKt" role="3o6s8t">
          <property role="2pNNFO" value="component" />
          <node concept="2b32R4" id="1KaxGo$cGVo" role="lGtFl">
            <node concept="3JmXsc" id="1KaxGo$cGVr" role="2P8S$">
              <node concept="3clFbS" id="1KaxGo$cGVs" role="2VODD2">
                <node concept="3clFbF" id="1KaxGo$cGVy" role="3cqZAp">
                  <node concept="2OqwBi" id="1KaxGo$cGVt" role="3clFbG">
                    <node concept="3Tsc0h" id="1KaxGo$cGVw" role="2OqNvi">
                      <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
                    </node>
                    <node concept="30H73N" id="1KaxGo$cGVx" role="2Oq$k0" />
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
    <node concept="n94m4" id="1KaxGo$aK99" role="lGtFl">
      <ref role="n9lRv" to="ktbj:5pu6noS52gF" resolve="ComponentSet" />
    </node>
    <node concept="17Uvod" id="1KaxGo$aK9a" role="lGtFl">
      <property role="2qtEX9" value="name" />
      <property role="P4ACc" value="ceab5195-25ea-4f22-9b92-103b95ca8c0c/1169194658468/1169194664001" />
      <node concept="3zFVjK" id="1KaxGo$aK9d" role="3zH0cK">
        <node concept="3clFbS" id="1KaxGo$aK9e" role="2VODD2">
          <node concept="3clFbF" id="1KaxGo$aK9k" role="3cqZAp">
            <node concept="2OqwBi" id="1KaxGo$aK9f" role="3clFbG">
              <node concept="3TrcHB" id="1KaxGo$aK9i" role="2OqNvi">
                <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
              </node>
              <node concept="30H73N" id="1KaxGo$aK9j" role="2Oq$k0" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="13MO4I" id="1KaxGo$aQ8w">
    <property role="TrG5h" value="reduce_Component" />
    <ref role="3gUMe" to="ktbj:5pu6noS5f54" resolve="Component" />
    <node concept="2pNNFK" id="1KaxGo$cBHz" role="13RCb5">
      <property role="2pNNFO" value="component" />
      <node concept="3o6iSG" id="1KaxGo$cBH$" role="3o6s8t" />
      <node concept="2pNNFK" id="1KaxGo$cBH_" role="3o6s8t">
        <property role="2pNNFO" value="subsystem_id" />
        <node concept="3o6iSG" id="1KaxGo$cBHA" role="3o6s8t">
          <property role="3o6i5n" value="id" />
          <node concept="17Uvod" id="1KaxGo$cBHB" role="lGtFl">
            <property role="2qtEX9" value="value" />
            <property role="P4ACc" value="479c7a8c-02f9-43b5-9139-d910cb22f298/1622293396948952339/1622293396948953704" />
            <node concept="3zFVjK" id="1KaxGo$cBHC" role="3zH0cK">
              <node concept="3clFbS" id="1KaxGo$cBHD" role="2VODD2">
                <node concept="3clFbF" id="1KaxGo$cBHE" role="3cqZAp">
                  <node concept="2OqwBi" id="1KaxGo$cBHF" role="3clFbG">
                    <node concept="30H73N" id="1KaxGo$cBHG" role="2Oq$k0" />
                    <node concept="3TrcHB" id="1KaxGo$cBHH" role="2OqNvi">
                      <ref role="3TsBF5" to="ktbj:74C6il$sxIF" resolve="subsystem" />
                    </node>
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
      <node concept="2pNNFK" id="1KaxGo$cBHI" role="3o6s8t">
        <property role="2pNNFO" value="dependencies" />
        <node concept="3o6iSG" id="1KaxGo$cBHJ" role="3o6s8t" />
        <node concept="2pNNFK" id="1KaxGo$cBHK" role="3o6s8t">
          <property role="2pNNFO" value="dependency" />
          <node concept="2b32R4" id="1KaxGo$cBHL" role="lGtFl">
            <node concept="3JmXsc" id="1KaxGo$cBHM" role="2P8S$">
              <node concept="3clFbS" id="1KaxGo$cBHN" role="2VODD2">
                <node concept="3clFbF" id="1KaxGo$cBHO" role="3cqZAp">
                  <node concept="2OqwBi" id="1KaxGo$cBHP" role="3clFbG">
                    <node concept="3Tsc0h" id="1KaxGo$cBHQ" role="2OqNvi">
                      <ref role="3TtcxE" to="ktbj:5pu6noS5f57" resolve="dep" />
                    </node>
                    <node concept="30H73N" id="1KaxGo$cBHR" role="2Oq$k0" />
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
      <node concept="2pNUuL" id="1KaxGo$cBHS" role="2pNNFR">
        <property role="2pNUuO" value="name" />
        <node concept="2pMdtt" id="1KaxGo$cBHT" role="2pMdts">
          <node concept="17Uvod" id="1KaxGo$cBHU" role="lGtFl">
            <property role="2qtEX9" value="text" />
            <property role="P4ACc" value="479c7a8c-02f9-43b5-9139-d910cb22f298/6666499814681541919/6666499814681541920" />
            <node concept="3zFVjK" id="1KaxGo$cBHV" role="3zH0cK">
              <node concept="3clFbS" id="1KaxGo$cBHW" role="2VODD2">
                <node concept="3clFbF" id="1KaxGo$cBHX" role="3cqZAp">
                  <node concept="2OqwBi" id="1KaxGo$cBHY" role="3clFbG">
                    <node concept="3TrcHB" id="1KaxGo$cBHZ" role="2OqNvi">
                      <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                    </node>
                    <node concept="30H73N" id="1KaxGo$cBI0" role="2Oq$k0" />
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
      <node concept="raruj" id="1KaxGo$cEVp" role="lGtFl" />
    </node>
  </node>
  <node concept="13MO4I" id="1KaxGo$b451">
    <property role="TrG5h" value="reduce_Dependency" />
    <ref role="3gUMe" to="ktbj:5pu6noS6R6w" resolve="Dependency" />
    <node concept="2pNNFK" id="1KaxGo$b45e" role="13RCb5">
      <property role="2pNNFO" value="dependsOn" />
      <node concept="raruj" id="1KaxGo$b45f" role="lGtFl" />
      <node concept="3o6iSG" id="1KaxGo$b45g" role="3o6s8t">
        <property role="3o6i5n" value="id" />
        <node concept="17Uvod" id="1KaxGo$b45j" role="lGtFl">
          <property role="2qtEX9" value="value" />
          <property role="P4ACc" value="479c7a8c-02f9-43b5-9139-d910cb22f298/1622293396948952339/1622293396948953704" />
          <node concept="3zFVjK" id="1KaxGo$b45k" role="3zH0cK">
            <node concept="3clFbS" id="1KaxGo$b45l" role="2VODD2">
              <node concept="3clFbF" id="1KaxGo$b4mq" role="3cqZAp">
                <node concept="2OqwBi" id="1KaxGo$b66m" role="3clFbG">
                  <node concept="2OqwBi" id="1KaxGo$b4xS" role="2Oq$k0">
                    <node concept="30H73N" id="1KaxGo$b4mp" role="2Oq$k0" />
                    <node concept="3TrEf2" id="1KaxGo$b5fp" role="2OqNvi">
                      <ref role="3Tt5mk" to="ktbj:5pu6noS6Rpk" resolve="to" />
                    </node>
                  </node>
                  <node concept="3TrcHB" id="1KaxGo$b6_N" role="2OqNvi">
                    <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
</model>

