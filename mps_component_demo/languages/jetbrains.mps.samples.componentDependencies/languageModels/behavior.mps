<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:2b855002-fb92-4fa1-acaa-ec457490e763(jetbrains.mps.samples.componentDependencies.behavior)">
  <persistence version="9" />
  <languages>
    <use id="af65afd8-f0dd-4942-87d9-63a55f2a9db1" name="jetbrains.mps.lang.behavior" version="2" />
    <devkit ref="fbc25dd2-5da4-483a-8b19-70928e1b62d7(jetbrains.mps.devkit.general-purpose)" />
  </languages>
  <imports>
    <import index="ktbj" ref="r:afaf73eb-94a1-4aae-902b-ed4d28124667(jetbrains.mps.samples.componentDependencies.structure)" />
    <import index="tpcu" ref="r:00000000-0000-4000-0000-011c89590282(jetbrains.mps.lang.core.behavior)" />
  </imports>
  <registry>
    <language id="af65afd8-f0dd-4942-87d9-63a55f2a9db1" name="jetbrains.mps.lang.behavior">
      <concept id="1225194240794" name="jetbrains.mps.lang.behavior.structure.ConceptBehavior" flags="ng" index="13h7C7">
        <reference id="1225194240799" name="concept" index="13h7C2" />
        <child id="1225194240805" name="method" index="13h7CS" />
        <child id="1225194240801" name="constructor" index="13h7CW" />
      </concept>
      <concept id="1225194413805" name="jetbrains.mps.lang.behavior.structure.ConceptConstructorDeclaration" flags="in" index="13hLZK" />
      <concept id="1225194472830" name="jetbrains.mps.lang.behavior.structure.ConceptMethodDeclaration" flags="ng" index="13i0hz" />
      <concept id="1225194691553" name="jetbrains.mps.lang.behavior.structure.ThisNodeExpression" flags="nn" index="13iPFW" />
    </language>
    <language id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage">
      <concept id="1215693861676" name="jetbrains.mps.baseLanguage.structure.BaseAssignmentExpression" flags="nn" index="d038R">
        <child id="1068498886297" name="rValue" index="37vLTx" />
        <child id="1068498886295" name="lValue" index="37vLTJ" />
      </concept>
      <concept id="4836112446988635817" name="jetbrains.mps.baseLanguage.structure.UndefinedType" flags="in" index="2jxLKc" />
      <concept id="1197027756228" name="jetbrains.mps.baseLanguage.structure.DotExpression" flags="nn" index="2OqwBi">
        <child id="1197027771414" name="operand" index="2Oq$k0" />
        <child id="1197027833540" name="operation" index="2OqNvi" />
      </concept>
      <concept id="1137021947720" name="jetbrains.mps.baseLanguage.structure.ConceptFunction" flags="in" index="2VMwT0">
        <child id="1137022507850" name="body" index="2VODD2" />
      </concept>
      <concept id="1068498886296" name="jetbrains.mps.baseLanguage.structure.VariableReference" flags="nn" index="37vLTw">
        <reference id="1068581517664" name="variableDeclaration" index="3cqZAo" />
      </concept>
      <concept id="1068498886294" name="jetbrains.mps.baseLanguage.structure.AssignmentExpression" flags="nn" index="37vLTI" />
      <concept id="4972933694980447171" name="jetbrains.mps.baseLanguage.structure.BaseVariableDeclaration" flags="ng" index="19Szcq">
        <child id="5680397130376446158" name="type" index="1tU5fm" />
      </concept>
      <concept id="1068580123132" name="jetbrains.mps.baseLanguage.structure.BaseMethodDeclaration" flags="ng" index="3clF44">
        <child id="1068580123133" name="returnType" index="3clF45" />
        <child id="1068580123135" name="body" index="3clF47" />
      </concept>
      <concept id="1068580123155" name="jetbrains.mps.baseLanguage.structure.ExpressionStatement" flags="nn" index="3clFbF">
        <child id="1068580123156" name="expression" index="3clFbG" />
      </concept>
      <concept id="1068580123136" name="jetbrains.mps.baseLanguage.structure.StatementList" flags="sn" stub="5293379017992965193" index="3clFbS">
        <child id="1068581517665" name="statement" index="3cqZAp" />
      </concept>
      <concept id="1068580320020" name="jetbrains.mps.baseLanguage.structure.IntegerConstant" flags="nn" index="3cmrfG">
        <property id="1068580320021" name="value" index="3cmrfH" />
      </concept>
      <concept id="1068581242878" name="jetbrains.mps.baseLanguage.structure.ReturnStatement" flags="nn" index="3cpWs6">
        <child id="1068581517676" name="expression" index="3cqZAk" />
      </concept>
      <concept id="1178549954367" name="jetbrains.mps.baseLanguage.structure.IVisible" flags="ngI" index="1B3ioH">
        <child id="1178549979242" name="visibility" index="1B3o_S" />
      </concept>
      <concept id="1146644602865" name="jetbrains.mps.baseLanguage.structure.PublicVisibility" flags="nn" index="3Tm1VV" />
    </language>
    <language id="fd392034-7849-419d-9071-12563d152375" name="jetbrains.mps.baseLanguage.closures">
      <concept id="2524418899405758586" name="jetbrains.mps.baseLanguage.closures.structure.InferredClosureParameterDeclaration" flags="ig" index="gl6BB" />
      <concept id="1199569711397" name="jetbrains.mps.baseLanguage.closures.structure.ClosureLiteral" flags="nn" index="1bVj0M">
        <child id="1199569906740" name="parameter" index="1bW2Oz" />
        <child id="1199569916463" name="body" index="1bW5cS" />
      </concept>
    </language>
    <language id="7866978e-a0f0-4cc7-81bc-4d213d9375e1" name="jetbrains.mps.lang.smodel">
      <concept id="1138055754698" name="jetbrains.mps.lang.smodel.structure.SNodeType" flags="in" index="3Tqbb2">
        <reference id="1138405853777" name="concept" index="ehGHo" />
      </concept>
      <concept id="1138056022639" name="jetbrains.mps.lang.smodel.structure.SPropertyAccess" flags="nn" index="3TrcHB">
        <reference id="1138056395725" name="property" index="3TsBF5" />
      </concept>
      <concept id="1138056282393" name="jetbrains.mps.lang.smodel.structure.SLinkListAccess" flags="nn" index="3Tsc0h">
        <reference id="1138056546658" name="link" index="3TtcxE" />
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ngI" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
    <language id="83888646-71ce-4f1c-9c53-c54016f6ad4f" name="jetbrains.mps.baseLanguage.collections">
      <concept id="1204796164442" name="jetbrains.mps.baseLanguage.collections.structure.InternalSequenceOperation" flags="nn" index="23sCx2">
        <child id="1204796294226" name="closure" index="23t8la" />
      </concept>
      <concept id="1151689724996" name="jetbrains.mps.baseLanguage.collections.structure.SequenceType" flags="in" index="A3Dl8">
        <child id="1151689745422" name="elementType" index="A3Ik2" />
      </concept>
      <concept id="1201792049884" name="jetbrains.mps.baseLanguage.collections.structure.TranslateOperation" flags="nn" index="3goQfb" />
    </language>
  </registry>
  <node concept="13h7C7" id="7SUlOxgz$az">
    <ref role="13h7C2" to="ktbj:5pu6noS52gF" resolve="ComponentSet" />
    <node concept="13i0hz" id="7SUlOxgz$bp" role="13h7CS">
      <property role="TrG5h" value="retrieveDependencies" />
      <node concept="3Tm1VV" id="7SUlOxgz$bq" role="1B3o_S" />
      <node concept="3clFbS" id="7SUlOxgz$bs" role="3clF47">
        <node concept="3cpWs6" id="7SUlOxgzCFv" role="3cqZAp">
          <node concept="2OqwBi" id="7SUlOxgzCTu" role="3cqZAk">
            <node concept="2OqwBi" id="7SUlOxgzCTv" role="2Oq$k0">
              <node concept="13iPFW" id="7SUlOxgzCTw" role="2Oq$k0" />
              <node concept="3Tsc0h" id="7SUlOxgzCTx" role="2OqNvi">
                <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
              </node>
            </node>
            <node concept="3goQfb" id="7SUlOxgzCTy" role="2OqNvi">
              <node concept="1bVj0M" id="7SUlOxgzCTz" role="23t8la">
                <node concept="3clFbS" id="7SUlOxgzCT$" role="1bW5cS">
                  <node concept="3clFbF" id="7SUlOxgzCT_" role="3cqZAp">
                    <node concept="2OqwBi" id="7SUlOxgzCTA" role="3clFbG">
                      <node concept="37vLTw" id="7SUlOxgzCTB" role="2Oq$k0">
                        <ref role="3cqZAo" node="5W7E4fV0WXz" resolve="it" />
                      </node>
                      <node concept="3Tsc0h" id="7SUlOxgzCTC" role="2OqNvi">
                        <ref role="3TtcxE" to="ktbj:5pu6noS5f57" resolve="dep" />
                      </node>
                    </node>
                  </node>
                </node>
                <node concept="gl6BB" id="5W7E4fV0WXz" role="1bW2Oz">
                  <property role="TrG5h" value="it" />
                  <node concept="2jxLKc" id="5W7E4fV0WX$" role="1tU5fm" />
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
      <node concept="A3Dl8" id="7SUlOxgzCQ$" role="3clF45">
        <node concept="3Tqbb2" id="7SUlOxgzCQ_" role="A3Ik2">
          <ref role="ehGHo" to="ktbj:5pu6noS6R6w" resolve="Dependency" />
        </node>
      </node>
    </node>
    <node concept="13hLZK" id="7SUlOxgz$a$" role="13h7CW">
      <node concept="3clFbS" id="7SUlOxgz$a_" role="2VODD2" />
    </node>
  </node>
  <node concept="13h7C7" id="7SUlOxgA$Jo">
    <ref role="13h7C2" to="ktbj:5pu6noS6R6w" resolve="Dependency" />
    <node concept="13hLZK" id="7SUlOxgA$Jp" role="13h7CW">
      <node concept="3clFbS" id="7SUlOxgA$Jq" role="2VODD2" />
    </node>
  </node>
  <node concept="13h7C7" id="7SUlOxgCdx1">
    <ref role="13h7C2" to="ktbj:5pu6noS5f54" resolve="Component" />
    <node concept="13hLZK" id="7SUlOxgCdx2" role="13h7CW">
      <node concept="3clFbS" id="7SUlOxgCdx3" role="2VODD2">
        <node concept="3clFbF" id="$6em42Pl4n" role="3cqZAp">
          <node concept="37vLTI" id="$6em42PlQI" role="3clFbG">
            <node concept="3cmrfG" id="$6em42PlQY" role="37vLTx">
              <property role="3cmrfH" value="100" />
            </node>
            <node concept="2OqwBi" id="$6em42Pl6I" role="37vLTJ">
              <node concept="13iPFW" id="$6em42Pl4m" role="2Oq$k0" />
              <node concept="3TrcHB" id="$6em42PlfL" role="2OqNvi">
                <ref role="3TsBF5" to="ktbj:5pu6noS6XHd" resolve="x" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="$6em42PmfW" role="3cqZAp">
          <node concept="37vLTI" id="$6em42Pn0C" role="3clFbG">
            <node concept="3cmrfG" id="$6em42Pn0S" role="37vLTx">
              <property role="3cmrfH" value="100" />
            </node>
            <node concept="2OqwBi" id="$6em42PmhF" role="37vLTJ">
              <node concept="13iPFW" id="$6em42PmfU" role="2Oq$k0" />
              <node concept="3TrcHB" id="$6em42PmqP" role="2OqNvi">
                <ref role="3TsBF5" to="ktbj:5pu6noS6XHf" resolve="y" />
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
</model>

