<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:7ef60438-f5cb-4ce3-b173-829ec8cb68a1(jetbrains.mps.samples.componentDependencies.editor)">
  <persistence version="9" />
  <languages>
    <use id="ed6d7656-532c-4bc2-81d1-af945aeb8280" name="jetbrains.mps.baseLanguage.blTypes" version="0" />
    <use id="443f4c36-fcf5-4eb6-9500-8d06ed259e3e" name="jetbrains.mps.baseLanguage.classifiers" version="0" />
    <use id="aee9cad2-acd4-4608-aef2-0004f6a1cdbd" name="jetbrains.mps.lang.actions" version="4" />
    <use id="6106f611-7a74-42d1-80de-edc5c602bfd1" name="jetbrains.mps.lang.editor.diagram" version="1" />
    <use id="d7722d50-4b93-4c3a-ae06-1903d05f95a7" name="jetbrains.mps.lang.editor.figures" version="0" />
    <use id="0272d3b4-4cc8-481e-9e2f-07793fbfcb41" name="jetbrains.mps.lang.editor.table" version="0" />
    <use id="13744753-c81f-424a-9c1b-cf8943bf4e86" name="jetbrains.mps.lang.sharedConcepts" version="0" />
    <use id="9ded098b-ad6a-4657-bfd9-48636cfe8bc3" name="jetbrains.mps.lang.traceable" version="0" />
    <use id="c72da2b9-7cce-4447-8389-f407dc1158b7" name="jetbrains.mps.lang.structure" version="9" />
    <use id="18bc6592-03a6-4e29-a83a-7ff23bde13ba" name="jetbrains.mps.lang.editor" version="15" />
    <devkit ref="fbc25dd2-5da4-483a-8b19-70928e1b62d7(jetbrains.mps.devkit.general-purpose)" />
  </languages>
  <imports>
    <import index="jqfx" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.projectional.view(jetbrains.jetpad/)" />
    <import index="8n5u" ref="r:05147575-afa1-4d0f-b2e0-f20b32ad3e33(jetbrains.mps.lang.editor.diagram.runtime.jetpad.views)" />
    <import index="4rj2" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.values(jetbrains.jetpad/)" />
    <import index="wyt6" ref="6354ebe7-c22a-4a0f-ac54-50b52ab9b065/java:java.lang(JDK/)" />
    <import index="lgza" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.model.property(jetbrains.jetpad/)" />
    <import index="33ny" ref="6354ebe7-c22a-4a0f-ac54-50b52ab9b065/java:java.util(JDK/)" />
    <import index="sm7x" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.mapper(jetbrains.jetpad/)" />
    <import index="77jp" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.cell.view(jetbrains.jetpad/)" />
    <import index="d7dq" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.cell(jetbrains.jetpad/)" />
    <import index="5v25" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.cell.text(jetbrains.jetpad/)" />
    <import index="g88e" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.geometry(jetbrains.jetpad/)" />
    <import index="squ6" ref="r:b60215f1-3d3e-41cc-8321-723ef8eb59dd(jetbrains.mps.lang.editor.table.runtime)" />
    <import index="f4zo" ref="1ed103c3-3aa6-49b7-9c21-6765ee11f224/java:jetbrains.mps.openapi.editor.cells(MPS.Editor/)" />
    <import index="ktbj" ref="r:afaf73eb-94a1-4aae-902b-ed4d28124667(jetbrains.mps.samples.componentDependencies.structure)" />
    <import index="okxs" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.projectional.diagram.view.layout(jetbrains.jetpad/)" />
    <import index="d0r4" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.cell.toView(jetbrains.jetpad/)" />
    <import index="8tro" ref="r:257a7f19-40a4-4037-a93b-ce1b638af281(jetbrains.mps.lang.editor.figures.library)" />
    <import index="chl9" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.base(jetbrains.jetpad/)" />
    <import index="zdnc" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.projectional.diagram.view(jetbrains.jetpad/)" />
    <import index="x7mh" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.model.event(jetbrains.jetpad/)" />
    <import index="mgas" ref="67b3c41d-58b3-4756-b971-30bf8a9d63e6/java:jetbrains.jetpad.projectional.diagram.base(jetbrains.jetpad/)" />
    <import index="8jsd" ref="r:18b1829d-108a-465e-a7a8-862d91582bc3(jetbrains.mps.nodeEditor.cells.jetpad)" />
    <import index="tpck" ref="r:00000000-0000-4000-0000-011c89590288(jetbrains.mps.lang.core.structure)" implicit="true" />
  </imports>
  <registry>
    <language id="18bc6592-03a6-4e29-a83a-7ff23bde13ba" name="jetbrains.mps.lang.editor">
      <concept id="1402906326895675325" name="jetbrains.mps.lang.editor.structure.CellActionMap_FunctionParm_selectedNode" flags="nn" index="0IXxy" />
      <concept id="1071666914219" name="jetbrains.mps.lang.editor.structure.ConceptEditorDeclaration" flags="ig" index="24kQdi">
        <child id="1078153129734" name="inspectedCellModel" index="6VMZX" />
        <child id="2597348684684069742" name="contextHints" index="CpUAK" />
      </concept>
      <concept id="6822301196700715228" name="jetbrains.mps.lang.editor.structure.ConceptEditorHintDeclarationReference" flags="ig" index="2aJ2om">
        <reference id="5944657839026714445" name="hint" index="2$4xQ3" />
      </concept>
      <concept id="1140524381322" name="jetbrains.mps.lang.editor.structure.CellModel_ListWithRole" flags="ng" index="2czfm3">
        <child id="1140524464360" name="cellLayout" index="2czzBx" />
      </concept>
      <concept id="1106270549637" name="jetbrains.mps.lang.editor.structure.CellLayout_Horizontal" flags="nn" index="2iRfu4" />
      <concept id="1106270571710" name="jetbrains.mps.lang.editor.structure.CellLayout_Vertical" flags="nn" index="2iRkQZ" />
      <concept id="1237303669825" name="jetbrains.mps.lang.editor.structure.CellLayout_Indent" flags="nn" index="l2Vlx" />
      <concept id="1237307900041" name="jetbrains.mps.lang.editor.structure.IndentLayoutIndentStyleClassItem" flags="ln" index="lj46D" />
      <concept id="1237308012275" name="jetbrains.mps.lang.editor.structure.IndentLayoutNewLineStyleClassItem" flags="ln" index="ljvvj" />
      <concept id="1237375020029" name="jetbrains.mps.lang.editor.structure.IndentLayoutNewLineChildrenStyleClassItem" flags="ln" index="pj6Ft" />
      <concept id="1142886221719" name="jetbrains.mps.lang.editor.structure.QueryFunction_NodeCondition" flags="in" index="pkWqt" />
      <concept id="1142886811589" name="jetbrains.mps.lang.editor.structure.ConceptFunctionParameter_node" flags="nn" index="pncrf" />
      <concept id="1080736578640" name="jetbrains.mps.lang.editor.structure.BaseEditorComponent" flags="ig" index="2wURMF">
        <child id="1080736633877" name="cellModel" index="2wV5jI" />
      </concept>
      <concept id="5944657839000868711" name="jetbrains.mps.lang.editor.structure.ConceptEditorContextHints" flags="ig" index="2ABfQD">
        <child id="5944657839000877563" name="hints" index="2ABdcP" />
      </concept>
      <concept id="5944657839003601246" name="jetbrains.mps.lang.editor.structure.ConceptEditorHintDeclaration" flags="ig" index="2BsEeg">
        <property id="168363875802087287" name="showInUI" index="2gpH_U" />
        <property id="5944657839012629576" name="presentation" index="2BUmq6" />
      </concept>
      <concept id="1186403694788" name="jetbrains.mps.lang.editor.structure.ColorStyleClassItem" flags="ln" index="VaVBg">
        <property id="1186403713874" name="color" index="Vb096" />
      </concept>
      <concept id="1186404549998" name="jetbrains.mps.lang.editor.structure.ForegroundColorStyleClassItem" flags="ln" index="VechU" />
      <concept id="1186414536763" name="jetbrains.mps.lang.editor.structure.BooleanStyleSheetItem" flags="ln" index="VOi$J">
        <property id="1186414551515" name="flag" index="VOm3f" />
      </concept>
      <concept id="1186414928363" name="jetbrains.mps.lang.editor.structure.SelectableStyleSheetItem" flags="ln" index="VPM3Z" />
      <concept id="1074767920765" name="jetbrains.mps.lang.editor.structure.CellModel_ModelAccess" flags="sg" stub="8104358048506729357" index="XafU7">
        <child id="1176718152741" name="modelAcessor" index="3TRxkO" />
      </concept>
      <concept id="1139535219966" name="jetbrains.mps.lang.editor.structure.CellActionMapDeclaration" flags="ig" index="1h_SRR">
        <reference id="1139535219968" name="applicableConcept" index="1h_SK9" />
        <child id="1139535219969" name="item" index="1h_SK8" />
      </concept>
      <concept id="1139535280617" name="jetbrains.mps.lang.editor.structure.CellActionMapItem" flags="lg" index="1hA7zw">
        <property id="1139535298778" name="actionId" index="1hAc7j" />
        <child id="1139535280620" name="executeFunction" index="1hA7z_" />
      </concept>
      <concept id="1139535439104" name="jetbrains.mps.lang.editor.structure.CellActionMap_ExecuteFunction" flags="in" index="1hAIg9" />
      <concept id="1088013125922" name="jetbrains.mps.lang.editor.structure.CellModel_RefCell" flags="sg" stub="730538219795941030" index="1iCGBv">
        <child id="1088186146602" name="editorComponent" index="1sWHZn" />
      </concept>
      <concept id="1088185857835" name="jetbrains.mps.lang.editor.structure.InlineEditorComponent" flags="ig" index="1sVBvm" />
      <concept id="1139848536355" name="jetbrains.mps.lang.editor.structure.CellModel_WithRole" flags="ng" index="1$h60E">
        <property id="1139852716018" name="noTargetText" index="1$x2rV" />
        <property id="1140017977771" name="readOnly" index="1Intyy" />
        <property id="1140114345053" name="allowEmptyText" index="1O74Pk" />
        <reference id="1140103550593" name="relationDeclaration" index="1NtTu8" />
      </concept>
      <concept id="1073389214265" name="jetbrains.mps.lang.editor.structure.EditorCellModel" flags="ng" index="3EYTF0">
        <reference id="1139959269582" name="actionMap" index="1ERwB7" />
        <child id="1142887637401" name="renderingCondition" index="pqm2j" />
      </concept>
      <concept id="1073389446423" name="jetbrains.mps.lang.editor.structure.CellModel_Collection" flags="sn" stub="3013115976261988961" index="3EZMnI">
        <child id="1106270802874" name="cellLayout" index="2iSdaV" />
        <child id="1073389446424" name="childCellModel" index="3EZMnx" />
      </concept>
      <concept id="1073389577006" name="jetbrains.mps.lang.editor.structure.CellModel_Constant" flags="sn" stub="3610246225209162225" index="3F0ifn">
        <property id="1073389577007" name="text" index="3F0ifm" />
      </concept>
      <concept id="1073389658414" name="jetbrains.mps.lang.editor.structure.CellModel_Property" flags="sg" stub="730538219796134133" index="3F0A7n" />
      <concept id="1219418625346" name="jetbrains.mps.lang.editor.structure.IStyleContainer" flags="ngI" index="3F0Thp">
        <child id="1219418656006" name="styleItem" index="3F10Kt" />
      </concept>
      <concept id="1073390211982" name="jetbrains.mps.lang.editor.structure.CellModel_RefNodeList" flags="sg" stub="2794558372793454595" index="3F2HdR" />
      <concept id="1176717841777" name="jetbrains.mps.lang.editor.structure.QueryFunction_ModelAccess_Getter" flags="in" index="3TQlhw" />
      <concept id="1176717871254" name="jetbrains.mps.lang.editor.structure.QueryFunction_ModelAccess_Setter" flags="in" index="3TQsA7" />
      <concept id="1176717888428" name="jetbrains.mps.lang.editor.structure.QueryFunction_ModelAccess_Validator" flags="in" index="3TQwEX" />
      <concept id="1176717996748" name="jetbrains.mps.lang.editor.structure.ModelAccessor" flags="ng" index="3TQVft">
        <child id="1176718001874" name="getter" index="3TQWv3" />
        <child id="1176718007938" name="setter" index="3TQXYj" />
        <child id="1176718014393" name="validator" index="3TQZqC" />
      </concept>
      <concept id="1198256887712" name="jetbrains.mps.lang.editor.structure.CellModel_Indent" flags="ng" index="3XFhqQ" />
      <concept id="1166049232041" name="jetbrains.mps.lang.editor.structure.AbstractComponent" flags="ng" index="1XWOmA">
        <reference id="1166049300910" name="conceptDeclaration" index="1XX52x" />
      </concept>
    </language>
    <language id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage">
      <concept id="1215693861676" name="jetbrains.mps.baseLanguage.structure.BaseAssignmentExpression" flags="nn" index="d038R">
        <child id="1068498886297" name="rValue" index="37vLTx" />
        <child id="1068498886295" name="lValue" index="37vLTJ" />
      </concept>
      <concept id="4836112446988635817" name="jetbrains.mps.baseLanguage.structure.UndefinedType" flags="in" index="2jxLKc" />
      <concept id="1202948039474" name="jetbrains.mps.baseLanguage.structure.InstanceMethodCallOperation" flags="nn" index="liA8E" />
      <concept id="1465982738277781862" name="jetbrains.mps.baseLanguage.structure.PlaceholderMember" flags="nn" index="2tJIrI" />
      <concept id="1076505808687" name="jetbrains.mps.baseLanguage.structure.WhileStatement" flags="nn" index="2$JKZl">
        <child id="1076505808688" name="condition" index="2$JKZa" />
      </concept>
      <concept id="1188207840427" name="jetbrains.mps.baseLanguage.structure.AnnotationInstance" flags="nn" index="2AHcQZ">
        <reference id="1188208074048" name="annotation" index="2AI5Lk" />
      </concept>
      <concept id="1188208481402" name="jetbrains.mps.baseLanguage.structure.HasAnnotation" flags="ngI" index="2AJDlI">
        <child id="1188208488637" name="annotation" index="2AJF6D" />
      </concept>
      <concept id="2820489544401957797" name="jetbrains.mps.baseLanguage.structure.DefaultClassCreator" flags="nn" index="HV5vD">
        <reference id="2820489544401957798" name="classifier" index="HV5vE" />
      </concept>
      <concept id="1154032098014" name="jetbrains.mps.baseLanguage.structure.AbstractLoopStatement" flags="nn" index="2LF5Ji">
        <child id="1154032183016" name="body" index="2LFqv$" />
      </concept>
      <concept id="1197027756228" name="jetbrains.mps.baseLanguage.structure.DotExpression" flags="nn" index="2OqwBi">
        <child id="1197027771414" name="operand" index="2Oq$k0" />
        <child id="1197027833540" name="operation" index="2OqNvi" />
      </concept>
      <concept id="1197029447546" name="jetbrains.mps.baseLanguage.structure.FieldReferenceOperation" flags="nn" index="2OwXpG">
        <reference id="1197029500499" name="fieldDeclaration" index="2Oxat5" />
      </concept>
      <concept id="1083260308424" name="jetbrains.mps.baseLanguage.structure.EnumConstantReference" flags="nn" index="Rm8GO">
        <reference id="1083260308426" name="enumConstantDeclaration" index="Rm8GQ" />
        <reference id="1144432896254" name="enumClass" index="1Px2BO" />
      </concept>
      <concept id="1145552977093" name="jetbrains.mps.baseLanguage.structure.GenericNewExpression" flags="nn" index="2ShNRf">
        <child id="1145553007750" name="creator" index="2ShVmc" />
      </concept>
      <concept id="1137021947720" name="jetbrains.mps.baseLanguage.structure.ConceptFunction" flags="in" index="2VMwT0">
        <child id="1137022507850" name="body" index="2VODD2" />
      </concept>
      <concept id="1070475354124" name="jetbrains.mps.baseLanguage.structure.ThisExpression" flags="nn" index="Xjq3P" />
      <concept id="1070475587102" name="jetbrains.mps.baseLanguage.structure.SuperConstructorInvocation" flags="nn" index="XkiVB" />
      <concept id="1070475926800" name="jetbrains.mps.baseLanguage.structure.StringLiteral" flags="nn" index="Xl_RD">
        <property id="1070475926801" name="value" index="Xl_RC" />
      </concept>
      <concept id="1182160077978" name="jetbrains.mps.baseLanguage.structure.AnonymousClassCreator" flags="nn" index="YeOm9">
        <child id="1182160096073" name="cls" index="YeSDq" />
      </concept>
      <concept id="1081236700937" name="jetbrains.mps.baseLanguage.structure.StaticMethodCall" flags="nn" index="2YIFZM">
        <reference id="1144433194310" name="classConcept" index="1Pybhc" />
      </concept>
      <concept id="1081256982272" name="jetbrains.mps.baseLanguage.structure.InstanceOfExpression" flags="nn" index="2ZW3vV">
        <child id="1081256993305" name="classType" index="2ZW6by" />
        <child id="1081256993304" name="leftExpression" index="2ZW6bz" />
      </concept>
      <concept id="1070533707846" name="jetbrains.mps.baseLanguage.structure.StaticFieldReference" flags="nn" index="10M0yZ">
        <reference id="1144433057691" name="classifier" index="1PxDUh" />
      </concept>
      <concept id="1070534058343" name="jetbrains.mps.baseLanguage.structure.NullLiteral" flags="nn" index="10Nm6u" />
      <concept id="1070534370425" name="jetbrains.mps.baseLanguage.structure.IntegerType" flags="in" index="10Oyi0" />
      <concept id="1070534644030" name="jetbrains.mps.baseLanguage.structure.BooleanType" flags="in" index="10P_77" />
      <concept id="1070534934090" name="jetbrains.mps.baseLanguage.structure.CastExpression" flags="nn" index="10QFUN">
        <child id="1070534934091" name="type" index="10QFUM" />
        <child id="1070534934092" name="expression" index="10QFUP" />
      </concept>
      <concept id="1068390468200" name="jetbrains.mps.baseLanguage.structure.FieldDeclaration" flags="ig" index="312cEg">
        <property id="8606350594693632173" name="isTransient" index="eg7rD" />
        <property id="1240249534625" name="isVolatile" index="34CwA1" />
      </concept>
      <concept id="1068390468198" name="jetbrains.mps.baseLanguage.structure.ClassConcept" flags="ig" index="312cEu">
        <property id="1075300953594" name="abstractClass" index="1sVAO0" />
        <property id="1221565133444" name="isFinal" index="1EXbeo" />
        <child id="1095933932569" name="implementedInterface" index="EKbjA" />
        <child id="1165602531693" name="superclass" index="1zkMxy" />
      </concept>
      <concept id="1068431474542" name="jetbrains.mps.baseLanguage.structure.VariableDeclaration" flags="ng" index="33uBYm">
        <property id="1176718929932" name="isFinal" index="3TUv4t" />
        <child id="1068431790190" name="initializer" index="33vP2m" />
      </concept>
      <concept id="1068498886296" name="jetbrains.mps.baseLanguage.structure.VariableReference" flags="nn" index="37vLTw">
        <reference id="1068581517664" name="variableDeclaration" index="3cqZAo" />
      </concept>
      <concept id="1068498886292" name="jetbrains.mps.baseLanguage.structure.ParameterDeclaration" flags="ir" index="37vLTG" />
      <concept id="1068498886294" name="jetbrains.mps.baseLanguage.structure.AssignmentExpression" flags="nn" index="37vLTI" />
      <concept id="1225271177708" name="jetbrains.mps.baseLanguage.structure.StringType" flags="in" index="17QB3L" />
      <concept id="1225271369338" name="jetbrains.mps.baseLanguage.structure.IsEmptyOperation" flags="nn" index="17RlXB" />
      <concept id="4972933694980447171" name="jetbrains.mps.baseLanguage.structure.BaseVariableDeclaration" flags="ng" index="19Szcq">
        <child id="5680397130376446158" name="type" index="1tU5fm" />
      </concept>
      <concept id="1068580123132" name="jetbrains.mps.baseLanguage.structure.BaseMethodDeclaration" flags="ng" index="3clF44">
        <property id="4276006055363816570" name="isSynchronized" index="od$2w" />
        <property id="1181808852946" name="isFinal" index="DiZV1" />
        <child id="1068580123133" name="returnType" index="3clF45" />
        <child id="1068580123134" name="parameter" index="3clF46" />
        <child id="1068580123135" name="body" index="3clF47" />
      </concept>
      <concept id="1068580123165" name="jetbrains.mps.baseLanguage.structure.InstanceMethodDeclaration" flags="ig" index="3clFb_">
        <property id="1178608670077" name="isAbstract" index="1EzhhJ" />
      </concept>
      <concept id="1068580123152" name="jetbrains.mps.baseLanguage.structure.EqualsExpression" flags="nn" index="3clFbC" />
      <concept id="1068580123155" name="jetbrains.mps.baseLanguage.structure.ExpressionStatement" flags="nn" index="3clFbF">
        <child id="1068580123156" name="expression" index="3clFbG" />
      </concept>
      <concept id="1068580123159" name="jetbrains.mps.baseLanguage.structure.IfStatement" flags="nn" index="3clFbJ">
        <child id="1068580123160" name="condition" index="3clFbw" />
        <child id="1068580123161" name="ifTrue" index="3clFbx" />
      </concept>
      <concept id="1068580123136" name="jetbrains.mps.baseLanguage.structure.StatementList" flags="sn" stub="5293379017992965193" index="3clFbS">
        <child id="1068581517665" name="statement" index="3cqZAp" />
      </concept>
      <concept id="1068580123137" name="jetbrains.mps.baseLanguage.structure.BooleanConstant" flags="nn" index="3clFbT">
        <property id="1068580123138" name="value" index="3clFbU" />
      </concept>
      <concept id="1068580123140" name="jetbrains.mps.baseLanguage.structure.ConstructorDeclaration" flags="ig" index="3clFbW" />
      <concept id="1068580320020" name="jetbrains.mps.baseLanguage.structure.IntegerConstant" flags="nn" index="3cmrfG">
        <property id="1068580320021" name="value" index="3cmrfH" />
      </concept>
      <concept id="1068581242875" name="jetbrains.mps.baseLanguage.structure.PlusExpression" flags="nn" index="3cpWs3" />
      <concept id="1068581242878" name="jetbrains.mps.baseLanguage.structure.ReturnStatement" flags="nn" index="3cpWs6">
        <child id="1068581517676" name="expression" index="3cqZAk" />
      </concept>
      <concept id="1068581242864" name="jetbrains.mps.baseLanguage.structure.LocalVariableDeclarationStatement" flags="nn" index="3cpWs8">
        <child id="1068581242865" name="localVariableDeclaration" index="3cpWs9" />
      </concept>
      <concept id="1068581242869" name="jetbrains.mps.baseLanguage.structure.MinusExpression" flags="nn" index="3cpWsd" />
      <concept id="1068581242863" name="jetbrains.mps.baseLanguage.structure.LocalVariableDeclaration" flags="nr" index="3cpWsn" />
      <concept id="1068581517677" name="jetbrains.mps.baseLanguage.structure.VoidType" flags="in" index="3cqZAl" />
      <concept id="1079359253375" name="jetbrains.mps.baseLanguage.structure.ParenthesizedExpression" flags="nn" index="1eOMI4">
        <child id="1079359253376" name="expression" index="1eOMHV" />
      </concept>
      <concept id="1204053956946" name="jetbrains.mps.baseLanguage.structure.IMethodCall" flags="ngI" index="1ndlxa">
        <reference id="1068499141037" name="baseMethodDeclaration" index="37wK5l" />
        <child id="1068499141038" name="actualArgument" index="37wK5m" />
      </concept>
      <concept id="1073063089578" name="jetbrains.mps.baseLanguage.structure.SuperMethodCall" flags="nn" index="3nyPlj" />
      <concept id="1212685548494" name="jetbrains.mps.baseLanguage.structure.ClassCreator" flags="nn" index="1pGfFk">
        <child id="1212687122400" name="typeParameter" index="1pMfVU" />
      </concept>
      <concept id="1107461130800" name="jetbrains.mps.baseLanguage.structure.Classifier" flags="ng" index="3pOWGL">
        <property id="521412098689998745" name="nonStatic" index="2bfB8j" />
        <child id="5375687026011219971" name="member" index="jymVt" unordered="true" />
      </concept>
      <concept id="1171903916106" name="jetbrains.mps.baseLanguage.structure.UpperBoundType" flags="in" index="3qUE_q">
        <child id="1171903916107" name="bound" index="3qUE_r" />
      </concept>
      <concept id="7812454656619025412" name="jetbrains.mps.baseLanguage.structure.LocalMethodCall" flags="nn" index="1rXfSq" />
      <concept id="1107535904670" name="jetbrains.mps.baseLanguage.structure.ClassifierType" flags="in" index="3uibUv">
        <reference id="1107535924139" name="classifier" index="3uigEE" />
        <child id="1109201940907" name="parameter" index="11_B2D" />
      </concept>
      <concept id="1081773326031" name="jetbrains.mps.baseLanguage.structure.BinaryOperation" flags="nn" index="3uHJSO">
        <child id="1081773367579" name="rightExpression" index="3uHU7w" />
        <child id="1081773367580" name="leftExpression" index="3uHU7B" />
      </concept>
      <concept id="1073239437375" name="jetbrains.mps.baseLanguage.structure.NotEqualsExpression" flags="nn" index="3y3z36" />
      <concept id="1178549954367" name="jetbrains.mps.baseLanguage.structure.IVisible" flags="ngI" index="1B3ioH">
        <child id="1178549979242" name="visibility" index="1B3o_S" />
      </concept>
      <concept id="1163668896201" name="jetbrains.mps.baseLanguage.structure.TernaryOperatorExpression" flags="nn" index="3K4zz7">
        <child id="1163668914799" name="condition" index="3K4Cdx" />
        <child id="1163668922816" name="ifTrue" index="3K4E3e" />
        <child id="1163668934364" name="ifFalse" index="3K4GZi" />
      </concept>
      <concept id="1146644602865" name="jetbrains.mps.baseLanguage.structure.PublicVisibility" flags="nn" index="3Tm1VV" />
      <concept id="1146644623116" name="jetbrains.mps.baseLanguage.structure.PrivateVisibility" flags="nn" index="3Tm6S6" />
      <concept id="1146644641414" name="jetbrains.mps.baseLanguage.structure.ProtectedVisibility" flags="nn" index="3Tmbuc" />
      <concept id="1178893518978" name="jetbrains.mps.baseLanguage.structure.ThisConstructorInvocation" flags="nn" index="1VxSAg" />
      <concept id="1080120340718" name="jetbrains.mps.baseLanguage.structure.AndExpression" flags="nn" index="1Wc70l" />
      <concept id="1170345865475" name="jetbrains.mps.baseLanguage.structure.AnonymousClass" flags="ig" index="1Y3b0j">
        <reference id="1170346070688" name="classifier" index="1Y3XeK" />
        <child id="1201186121363" name="typeParameter" index="2Ghqu4" />
      </concept>
    </language>
    <language id="fd392034-7849-419d-9071-12563d152375" name="jetbrains.mps.baseLanguage.closures">
      <concept id="2524418899405758586" name="jetbrains.mps.baseLanguage.closures.structure.InferredClosureParameterDeclaration" flags="ig" index="gl6BB" />
      <concept id="1199569711397" name="jetbrains.mps.baseLanguage.closures.structure.ClosureLiteral" flags="nn" index="1bVj0M">
        <child id="1199569906740" name="parameter" index="1bW2Oz" />
        <child id="1199569916463" name="body" index="1bW5cS" />
      </concept>
    </language>
    <language id="6106f611-7a74-42d1-80de-edc5c602bfd1" name="jetbrains.mps.lang.editor.diagram">
      <concept id="1094405431463454433" name="jetbrains.mps.lang.editor.diagram.structure.CellModel_DiagramNode" flags="sg" stub="730538219795610279" index="9$NOg">
        <child id="1094405431463455193" name="figure" index="9$N8C" />
        <child id="1094405431463761842" name="parameters" index="9_WL3" />
        <child id="2084788800269090635" name="inputPort" index="zbHsl" />
        <child id="2084788800269090678" name="outputPort" index="zbHsC" />
      </concept>
      <concept id="1094405431463761863" name="jetbrains.mps.lang.editor.diagram.structure.FigureParameterMapping" flags="ng" index="9_WKQ">
        <child id="285670992218957021" name="argument" index="3YbGMt" />
      </concept>
      <concept id="6306886970791033847" name="jetbrains.mps.lang.editor.diagram.structure.CellModel_Diagram" flags="sg" stub="730538219795567478" index="2b3QIZ">
        <child id="8570854907290721333" name="elementsCreation" index="3cyXsl" />
        <child id="5355858557208539148" name="diagramElements" index="1VXmjR" />
      </concept>
      <concept id="1301388602725986966" name="jetbrains.mps.lang.editor.diagram.structure.AbstractDiagramCreation" flags="ng" index="mdwis">
        <child id="1301388602726005547" name="query" index="mdGOx" />
      </concept>
      <concept id="6382742553261733065" name="jetbrains.mps.lang.editor.diagram.structure.CellModel_DiagramConnector" flags="sg" stub="730538219795610242" index="2FuRD1">
        <child id="1220375669566529919" name="input" index="2PTkhb" />
        <child id="1220375669566529925" name="output" index="2PTkiL" />
      </concept>
      <concept id="1220375669566347117" name="jetbrains.mps.lang.editor.diagram.structure.ConnectionEndBLQuery" flags="ng" index="2PTV9p">
        <child id="2915596886892604954" name="targetNode" index="3B0qBL" />
      </concept>
      <concept id="8570854907290423690" name="jetbrains.mps.lang.editor.diagram.structure.DiagramElementsCreation" flags="ng" index="3cx5EE">
        <child id="8570854907290527457" name="handler" index="3cxIR1" />
      </concept>
      <concept id="8570854907290527479" name="jetbrains.mps.lang.editor.diagram.structure.DiagramElementCreationHandler" flags="ig" index="3cxIRn" />
      <concept id="8570854907290717922" name="jetbrains.mps.lang.editor.diagram.structure.XFunctionParameter" flags="ng" index="3cyWn2" />
      <concept id="8570854907290717911" name="jetbrains.mps.lang.editor.diagram.structure.YFunctionParameter" flags="ng" index="3cyWnR" />
      <concept id="8570854907290717918" name="jetbrains.mps.lang.editor.diagram.structure.NodeFunctionParameter" flags="ng" index="3cyWnY" />
      <concept id="5422656561926747342" name="jetbrains.mps.lang.editor.diagram.structure.AttributedFigureReference" flags="ng" index="3FP96B">
        <reference id="5422656561931890753" name="figureAttribute" index="3FDhkC" />
      </concept>
      <concept id="3229274890673749551" name="jetbrains.mps.lang.editor.diagram.structure.ThisEditorNodeExpression" flags="ng" index="1SoGT8" />
      <concept id="5355858557208817201" name="jetbrains.mps.lang.editor.diagram.structure.DiagramElementBLQuery" flags="ng" index="1VYjFa">
        <child id="5355858557208817241" name="query" index="1VYjEy" />
      </concept>
      <concept id="285670992217672837" name="jetbrains.mps.lang.editor.diagram.structure.PropertyArgument" flags="ng" index="3YcAj5">
        <reference id="285670992217689748" name="property" index="3Ycyrk" />
      </concept>
      <concept id="285670992213637559" name="jetbrains.mps.lang.editor.diagram.structure.LinkArgument" flags="ng" index="3Ys17R">
        <reference id="285670992217679783" name="link" index="3Yc$ZB" />
      </concept>
      <concept id="285670992205972098" name="jetbrains.mps.lang.editor.diagram.structure.CellModel_DiagramPort" flags="sg" stub="730538219795610316" index="3YTeF2">
        <property id="285670992206001471" name="input" index="3YT9PZ" />
      </concept>
    </language>
    <language id="d7722d50-4b93-4c3a-ae06-1903d05f95a7" name="jetbrains.mps.lang.editor.figures">
      <concept id="2084788800270473556" name="jetbrains.mps.lang.editor.figures.structure.FigureParameterAttributeMethod" flags="ng" index="zeN4a" />
      <concept id="5422656561926747556" name="jetbrains.mps.lang.editor.figures.structure.FigureAttribute" flags="ng" index="3FP93d" />
    </language>
    <language id="7866978e-a0f0-4cc7-81bc-4d213d9375e1" name="jetbrains.mps.lang.smodel">
      <concept id="1177026924588" name="jetbrains.mps.lang.smodel.structure.RefConcept_Reference" flags="nn" index="chp4Y">
        <reference id="1177026940964" name="conceptDeclaration" index="cht4Q" />
      </concept>
      <concept id="1138411891628" name="jetbrains.mps.lang.smodel.structure.SNodeOperation" flags="nn" index="eCIE_">
        <child id="1144104376918" name="parameter" index="1xVPHs" />
      </concept>
      <concept id="2396822768958367367" name="jetbrains.mps.lang.smodel.structure.AbstractTypeCastExpression" flags="nn" index="$5XWr">
        <child id="6733348108486823193" name="leftExpression" index="1m5AlR" />
        <child id="3906496115198199033" name="conceptArgument" index="3oSUPX" />
      </concept>
      <concept id="1171407110247" name="jetbrains.mps.lang.smodel.structure.Node_GetAncestorOperation" flags="nn" index="2Xjw5R" />
      <concept id="1139613262185" name="jetbrains.mps.lang.smodel.structure.Node_GetParentOperation" flags="nn" index="1mfA1w" />
      <concept id="1144101972840" name="jetbrains.mps.lang.smodel.structure.OperationParm_Concept" flags="ng" index="1xMEDy">
        <child id="1207343664468" name="conceptArgument" index="ri$Ld" />
      </concept>
      <concept id="1140137987495" name="jetbrains.mps.lang.smodel.structure.SNodeTypeCastExpression" flags="nn" index="1PxgMI" />
      <concept id="1138055754698" name="jetbrains.mps.lang.smodel.structure.SNodeType" flags="in" index="3Tqbb2">
        <reference id="1138405853777" name="concept" index="ehGHo" />
      </concept>
      <concept id="1138056022639" name="jetbrains.mps.lang.smodel.structure.SPropertyAccess" flags="nn" index="3TrcHB">
        <reference id="1138056395725" name="property" index="3TsBF5" />
      </concept>
      <concept id="1138056143562" name="jetbrains.mps.lang.smodel.structure.SLinkAccess" flags="nn" index="3TrEf2">
        <reference id="1138056516764" name="link" index="3Tt5mk" />
      </concept>
      <concept id="1138056282393" name="jetbrains.mps.lang.smodel.structure.SLinkListAccess" flags="nn" index="3Tsc0h">
        <reference id="1138056546658" name="link" index="3TtcxE" />
      </concept>
      <concept id="1228341669568" name="jetbrains.mps.lang.smodel.structure.Node_DetachOperation" flags="nn" index="3YRAZt" />
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1133920641626" name="jetbrains.mps.lang.core.structure.BaseConcept" flags="ng" index="2VYdi">
        <property id="1193676396447" name="virtualPackage" index="3GE5qa" />
        <child id="5169995583184591170" name="smodelAttribute" index="lGtFl" />
      </concept>
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ngI" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
    <language id="0272d3b4-4cc8-481e-9e2f-07793fbfcb41" name="jetbrains.mps.lang.editor.table">
      <concept id="4490468428501056077" name="jetbrains.mps.lang.editor.table.structure.QueryFunction_TableModel" flags="in" index="2XI2dN" />
      <concept id="4677325677876400523" name="jetbrains.mps.lang.editor.table.structure.CellModel_Table" flags="ng" index="1CiYdB">
        <child id="4490468428501048483" name="tableModel" index="2XI0mt" />
      </concept>
    </language>
    <language id="83888646-71ce-4f1c-9c53-c54016f6ad4f" name="jetbrains.mps.baseLanguage.collections">
      <concept id="1204796164442" name="jetbrains.mps.baseLanguage.collections.structure.InternalSequenceOperation" flags="nn" index="23sCx2">
        <child id="1204796294226" name="closure" index="23t8la" />
      </concept>
      <concept id="540871147943773365" name="jetbrains.mps.baseLanguage.collections.structure.SingleArgumentSequenceOperation" flags="nn" index="25WWJ4">
        <child id="540871147943773366" name="argument" index="25WWJ7" />
      </concept>
      <concept id="1204980550705" name="jetbrains.mps.baseLanguage.collections.structure.VisitAllOperation" flags="nn" index="2es0OD" />
      <concept id="1151688443754" name="jetbrains.mps.baseLanguage.collections.structure.ListType" flags="in" index="_YKpA">
        <child id="1151688676805" name="elementType" index="_ZDj9" />
      </concept>
      <concept id="1151702311717" name="jetbrains.mps.baseLanguage.collections.structure.ToListOperation" flags="nn" index="ANE8D" />
      <concept id="1162934736510" name="jetbrains.mps.baseLanguage.collections.structure.GetElementOperation" flags="nn" index="34jXtK" />
      <concept id="1201792049884" name="jetbrains.mps.baseLanguage.collections.structure.TranslateOperation" flags="nn" index="3goQfb" />
      <concept id="1165525191778" name="jetbrains.mps.baseLanguage.collections.structure.GetFirstOperation" flags="nn" index="1uHKPH" />
      <concept id="1165530316231" name="jetbrains.mps.baseLanguage.collections.structure.IsEmptyOperation" flags="nn" index="1v1jN8" />
      <concept id="1225727723840" name="jetbrains.mps.baseLanguage.collections.structure.FindFirstOperation" flags="nn" index="1z4cxt" />
      <concept id="1202120902084" name="jetbrains.mps.baseLanguage.collections.structure.WhereOperation" flags="nn" index="3zZkjj" />
    </language>
  </registry>
  <node concept="24kQdi" id="5pu6noS68qF">
    <ref role="1XX52x" to="ktbj:5pu6noS52gF" resolve="ComponentSet" />
    <node concept="2b3QIZ" id="5pu6noS6cCb" role="2wV5jI">
      <node concept="3cx5EE" id="7SUlOxgyxE1" role="3cyXsl">
        <property role="TrG5h" value="New Component" />
        <node concept="3cxIRn" id="7SUlOxgyxE2" role="3cxIR1">
          <node concept="3clFbS" id="7SUlOxgyxE3" role="2VODD2">
            <node concept="3clFbF" id="7SUlOxgyDgL" role="3cqZAp">
              <node concept="37vLTI" id="7SUlOxgyDS9" role="3clFbG">
                <node concept="Xl_RD" id="7SUlOxgyDSr" role="37vLTx">
                  <property role="Xl_RC" value="New component" />
                </node>
                <node concept="2OqwBi" id="7SUlOxgyDij" role="37vLTJ">
                  <node concept="3cyWnY" id="7SUlOxgyDgK" role="2Oq$k0" />
                  <node concept="3TrcHB" id="7SUlOxgyDAw" role="2OqNvi">
                    <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="3clFbF" id="7SUlOxgyEes" role="3cqZAp">
              <node concept="37vLTI" id="7SUlOxgyF2_" role="3clFbG">
                <node concept="3cyWn2" id="$6em42PuZX" role="37vLTx" />
                <node concept="2OqwBi" id="7SUlOxgyEg1" role="37vLTJ">
                  <node concept="3cyWnY" id="7SUlOxgyEeq" role="2Oq$k0" />
                  <node concept="3TrcHB" id="7SUlOxgyEqg" role="2OqNvi">
                    <ref role="3TsBF5" to="ktbj:5pu6noS6XHd" resolve="x" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="3clFbF" id="7SUlOxgyFl2" role="3cqZAp">
              <node concept="37vLTI" id="7SUlOxgyG0O" role="3clFbG">
                <node concept="3cyWnR" id="$6em42Pvn7" role="37vLTx" />
                <node concept="2OqwBi" id="7SUlOxgyFmE" role="37vLTJ">
                  <node concept="3cyWnY" id="7SUlOxgyFl0" role="2Oq$k0" />
                  <node concept="3TrcHB" id="7SUlOxgyFxc" role="2OqNvi">
                    <ref role="3TsBF5" to="ktbj:5pu6noS6XHf" resolve="y" />
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="2OqwBi" id="7SUlOxgyBji" role="mdGOx">
          <node concept="1SoGT8" id="7SUlOxgyAJc" role="2Oq$k0" />
          <node concept="3Tsc0h" id="7SUlOxgyBBc" role="2OqNvi">
            <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
          </node>
        </node>
      </node>
      <node concept="1VYjFa" id="5pu6noS6cCo" role="1VXmjR">
        <node concept="2OqwBi" id="5pu6noS6fBC" role="1VYjEy">
          <node concept="1SoGT8" id="5pu6noS6cCu" role="2Oq$k0" />
          <node concept="3Tsc0h" id="5pu6noS6uTS" role="2OqNvi">
            <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
          </node>
        </node>
      </node>
      <node concept="1VYjFa" id="5pu6noS6uVs" role="1VXmjR">
        <node concept="2OqwBi" id="5pu6noS6MzK" role="1VYjEy">
          <node concept="2OqwBi" id="5pu6noS6uX8" role="2Oq$k0">
            <node concept="1SoGT8" id="5pu6noS6uVA" role="2Oq$k0" />
            <node concept="3Tsc0h" id="5pu6noS6v7i" role="2OqNvi">
              <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
            </node>
          </node>
          <node concept="3goQfb" id="5pu6noS6PbQ" role="2OqNvi">
            <node concept="1bVj0M" id="5pu6noS6PbS" role="23t8la">
              <node concept="3clFbS" id="5pu6noS6PbT" role="1bW5cS">
                <node concept="3clFbF" id="5pu6noS6Pmi" role="3cqZAp">
                  <node concept="2OqwBi" id="5pu6noS6PyT" role="3clFbG">
                    <node concept="37vLTw" id="5pu6noS6Pmh" role="2Oq$k0">
                      <ref role="3cqZAo" node="5W7E4fV0WX_" resolve="it" />
                    </node>
                    <node concept="3Tsc0h" id="5pu6noS78B0" role="2OqNvi">
                      <ref role="3TtcxE" to="ktbj:5pu6noS5f57" resolve="dep" />
                    </node>
                  </node>
                </node>
              </node>
              <node concept="gl6BB" id="5W7E4fV0WX_" role="1bW2Oz">
                <property role="TrG5h" value="it" />
                <node concept="2jxLKc" id="5W7E4fV0WXA" role="1tU5fm" />
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
    <node concept="2aJ2om" id="5pu6noS9Zrc" role="CpUAK">
      <ref role="2$4xQ3" node="5pu6noS9YPC" resolve="diagram" />
    </node>
  </node>
  <node concept="24kQdi" id="5pu6noS6R6S">
    <ref role="1XX52x" to="ktbj:5pu6noS6R6w" resolve="Dependency" />
    <node concept="2FuRD1" id="5pu6noS6R6U" role="2wV5jI">
      <ref role="1ERwB7" node="6sC7QXwVfkA" resolve="delConnector" />
      <node concept="2PTV9p" id="5pu6noS6R73" role="2PTkhb">
        <node concept="2OqwBi" id="16YoZ8JBkp4" role="3B0qBL">
          <node concept="2OqwBi" id="16YoZ8JAJHb" role="2Oq$k0">
            <node concept="1PxgMI" id="7SUlOxgBbO1" role="2Oq$k0">
              <node concept="2OqwBi" id="7SUlOxgxSIX" role="1m5AlR">
                <node concept="1SoGT8" id="7SUlOxgxSHj" role="2Oq$k0" />
                <node concept="1mfA1w" id="7SUlOxgBbEM" role="2OqNvi" />
              </node>
              <node concept="chp4Y" id="714IaVdH1_8" role="3oSUPX">
                <ref role="cht4Q" to="ktbj:5pu6noS5f54" resolve="Component" />
              </node>
            </node>
            <node concept="3Tsc0h" id="16YoZ8JAJTu" role="2OqNvi">
              <ref role="3TtcxE" to="ktbj:5pu6noS6Y56" resolve="out" />
            </node>
          </node>
          <node concept="1z4cxt" id="74C6il$lenl" role="2OqNvi">
            <node concept="1bVj0M" id="74C6il$lenn" role="23t8la">
              <node concept="3clFbS" id="74C6il$leno" role="1bW5cS">
                <node concept="3clFbF" id="74C6il$lesD" role="3cqZAp">
                  <node concept="2OqwBi" id="74C6il$lfc4" role="3clFbG">
                    <node concept="2OqwBi" id="74C6il$lewg" role="2Oq$k0">
                      <node concept="37vLTw" id="74C6il$lesC" role="2Oq$k0">
                        <ref role="3cqZAo" node="5W7E4fV0WXB" resolve="it" />
                      </node>
                      <node concept="3TrcHB" id="74C6il$leKh" role="2OqNvi">
                        <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                      </node>
                    </node>
                    <node concept="liA8E" id="74C6il$lgeU" role="2OqNvi">
                      <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                      <node concept="2OqwBi" id="74C6il$lh2m" role="37wK5m">
                        <node concept="2OqwBi" id="74C6il$lgru" role="2Oq$k0">
                          <node concept="1SoGT8" id="74C6il$lgkY" role="2Oq$k0" />
                          <node concept="3TrEf2" id="74C6il$lgDT" role="2OqNvi">
                            <ref role="3Tt5mk" to="ktbj:5pu6noS6Rpk" resolve="to" />
                          </node>
                        </node>
                        <node concept="3TrcHB" id="74C6il$lhsQ" role="2OqNvi">
                          <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                        </node>
                      </node>
                    </node>
                  </node>
                </node>
              </node>
              <node concept="gl6BB" id="5W7E4fV0WXB" role="1bW2Oz">
                <property role="TrG5h" value="it" />
                <node concept="2jxLKc" id="5W7E4fV0WXC" role="1tU5fm" />
              </node>
            </node>
          </node>
        </node>
      </node>
      <node concept="2PTV9p" id="5pu6noS6R79" role="2PTkiL">
        <node concept="2OqwBi" id="16YoZ8JBm8b" role="3B0qBL">
          <node concept="2OqwBi" id="16YoZ8JAKbL" role="2Oq$k0">
            <node concept="2OqwBi" id="5pu6noS6RGn" role="2Oq$k0">
              <node concept="1SoGT8" id="5pu6noS6RFb" role="2Oq$k0" />
              <node concept="3TrEf2" id="5pu6noS6RX3" role="2OqNvi">
                <ref role="3Tt5mk" to="ktbj:5pu6noS6Rpk" resolve="to" />
              </node>
            </node>
            <node concept="3Tsc0h" id="16YoZ8JAKvx" role="2OqNvi">
              <ref role="3TtcxE" to="ktbj:5pu6noS6Y52" resolve="in" />
            </node>
          </node>
          <node concept="1z4cxt" id="74C6il$lo9j" role="2OqNvi">
            <node concept="1bVj0M" id="74C6il$lo9l" role="23t8la">
              <node concept="3clFbS" id="74C6il$lo9m" role="1bW5cS">
                <node concept="3clFbF" id="74C6il$loeB" role="3cqZAp">
                  <node concept="2OqwBi" id="74C6il$lp5U" role="3clFbG">
                    <node concept="2OqwBi" id="74C6il$loie" role="2Oq$k0">
                      <node concept="37vLTw" id="74C6il$loeA" role="2Oq$k0">
                        <ref role="3cqZAo" node="5W7E4fV0WXD" resolve="it" />
                      </node>
                      <node concept="3TrcHB" id="74C6il$loyg" role="2OqNvi">
                        <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                      </node>
                    </node>
                    <node concept="liA8E" id="74C6il$lq8K" role="2OqNvi">
                      <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                      <node concept="2OqwBi" id="74C6il$lro0" role="37wK5m">
                        <node concept="1PxgMI" id="74C6il$lr29" role="2Oq$k0">
                          <node concept="2OqwBi" id="74C6il$lqtg" role="1m5AlR">
                            <node concept="1SoGT8" id="74C6il$lqeQ" role="2Oq$k0" />
                            <node concept="1mfA1w" id="74C6il$lqFF" role="2OqNvi" />
                          </node>
                          <node concept="chp4Y" id="714IaVdH1_7" role="3oSUPX">
                            <ref role="cht4Q" to="ktbj:5pu6noS5f54" resolve="Component" />
                          </node>
                        </node>
                        <node concept="3TrcHB" id="74C6il$lrQC" role="2OqNvi">
                          <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                        </node>
                      </node>
                    </node>
                  </node>
                </node>
              </node>
              <node concept="gl6BB" id="5W7E4fV0WXD" role="1bW2Oz">
                <property role="TrG5h" value="it" />
                <node concept="2jxLKc" id="5W7E4fV0WXE" role="1tU5fm" />
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
    <node concept="2aJ2om" id="5pu6noS9ZvG" role="CpUAK">
      <ref role="2$4xQ3" node="5pu6noS9YPC" resolve="diagram" />
    </node>
  </node>
  <node concept="24kQdi" id="5pu6noS6RXI">
    <ref role="1XX52x" to="ktbj:5pu6noS5f54" resolve="Component" />
    <node concept="9$NOg" id="5pu6noS6RXK" role="2wV5jI">
      <ref role="1ERwB7" node="6sC7QXwUVIu" resolve="delComponent" />
      <node concept="9_WKQ" id="2CIEV4adsil" role="9_WL3">
        <property role="TrG5h" value="nameText" />
        <node concept="3YcAj5" id="74C6il$tV1s" role="3YbGMt">
          <ref role="3Ycyrk" to="ktbj:74C6il$sxIF" resolve="subsystem" />
        </node>
      </node>
      <node concept="9_WKQ" id="74C6il$t$ly" role="9_WL3">
        <property role="TrG5h" value="idText" />
        <node concept="3YcAj5" id="74C6il$tV27" role="3YbGMt">
          <ref role="3Ycyrk" to="tpck:h0TrG11" resolve="name" />
        </node>
      </node>
      <node concept="9_WKQ" id="7SUlOxgvPZf" role="9_WL3">
        <property role="TrG5h" value="POSITION_X" />
        <node concept="3YcAj5" id="7SUlOxgvQ4u" role="3YbGMt">
          <ref role="3Ycyrk" to="ktbj:5pu6noS6XHd" resolve="x" />
        </node>
      </node>
      <node concept="9_WKQ" id="7SUlOxgvQ5c" role="9_WL3">
        <property role="TrG5h" value="POSITION_Y" />
        <node concept="3YcAj5" id="7SUlOxgvQb6" role="3YbGMt">
          <ref role="3Ycyrk" to="ktbj:5pu6noS6XHf" resolve="y" />
        </node>
      </node>
      <node concept="9_WKQ" id="74C6il$szZD" role="9_WL3">
        <property role="TrG5h" value="figureHeight" />
        <node concept="3YcAj5" id="74C6il$s$L1" role="3YbGMt">
          <ref role="3Ycyrk" to="ktbj:74C6il$sxIf" resolve="heigh" />
        </node>
      </node>
      <node concept="9_WKQ" id="74C6il$s$LI" role="9_WL3">
        <property role="TrG5h" value="figureWidth" />
        <node concept="3YcAj5" id="74C6il$s_$8" role="3YbGMt">
          <ref role="3Ycyrk" to="ktbj:74C6il$sxI8" resolve="width" />
        </node>
      </node>
      <node concept="3FP96B" id="74C6il$nAbk" role="9$N8C">
        <ref role="3FDhkC" node="HEilRNywb_" />
      </node>
      <node concept="3Ys17R" id="74C6il$ljqt" role="zbHsC">
        <ref role="3Yc$ZB" to="ktbj:5pu6noS6Y56" resolve="out" />
      </node>
      <node concept="3Ys17R" id="74C6il$livf" role="zbHsl">
        <ref role="3Yc$ZB" to="ktbj:5pu6noS6Y52" resolve="in" />
      </node>
    </node>
    <node concept="2aJ2om" id="5pu6noS9Ztw" role="CpUAK">
      <ref role="2$4xQ3" node="5pu6noS9YPC" resolve="diagram" />
    </node>
  </node>
  <node concept="24kQdi" id="5pu6noS9YMV">
    <ref role="1XX52x" to="ktbj:5pu6noS52gF" resolve="ComponentSet" />
    <node concept="3EZMnI" id="5pu6noS9YNg" role="2wV5jI">
      <node concept="2iRkQZ" id="5pu6noS9YNh" role="2iSdaV" />
      <node concept="3EZMnI" id="6sC7QXwU3vK" role="3EZMnx">
        <node concept="2iRfu4" id="6sC7QXwU3vL" role="2iSdaV" />
        <node concept="3F0ifn" id="6sC7QXwU3v6" role="3EZMnx">
          <property role="3F0ifm" value="name filter:" />
          <node concept="VechU" id="6sC7QXwU3xO" role="3F10Kt">
            <property role="Vb096" value="g1_qRwE/DARK_GREEN" />
          </node>
        </node>
        <node concept="3F0A7n" id="6sC7QXwU3w5" role="3EZMnx">
          <property role="1O74Pk" value="true" />
          <property role="1$x2rV" value="&lt;no filter&gt;" />
          <ref role="1NtTu8" to="ktbj:6sC7QXwR9qu" resolve="query" />
          <node concept="VechU" id="6sC7QXwU3xW" role="3F10Kt">
            <property role="Vb096" value="g1_qRwE/DARK_GREEN" />
          </node>
        </node>
      </node>
      <node concept="3EZMnI" id="5pu6noS9YN4" role="3EZMnx">
        <node concept="2iRfu4" id="5pu6noS9YN5" role="2iSdaV" />
        <node concept="3F0ifn" id="5pu6noS9YN2" role="3EZMnx">
          <property role="3F0ifm" value="component set" />
        </node>
        <node concept="3F0A7n" id="5pu6noS9YNd" role="3EZMnx">
          <ref role="1NtTu8" to="tpck:h0TrG11" resolve="name" />
        </node>
      </node>
      <node concept="3EZMnI" id="5pu6noS9YNE" role="3EZMnx">
        <node concept="3XFhqQ" id="5pu6noS9YNU" role="3EZMnx" />
        <node concept="2iRfu4" id="5pu6noS9YNF" role="2iSdaV" />
        <node concept="3F2HdR" id="5pu6noS9YNy" role="3EZMnx">
          <ref role="1NtTu8" to="ktbj:5pu6noS56YC" resolve="component" />
          <node concept="2iRkQZ" id="5pu6noS9YNz" role="2czzBx" />
        </node>
      </node>
    </node>
  </node>
  <node concept="2ABfQD" id="5pu6noS9YPB">
    <property role="TrG5h" value="views" />
    <node concept="2BsEeg" id="5pu6noS9YPC" role="2ABdcP">
      <property role="2gpH_U" value="true" />
      <property role="TrG5h" value="diagram" />
      <property role="2BUmq6" value="Diagram View" />
    </node>
    <node concept="2BsEeg" id="54Q_hb054Do" role="2ABdcP">
      <property role="2gpH_U" value="true" />
      <property role="TrG5h" value="table" />
      <property role="2BUmq6" value="Table View" />
    </node>
  </node>
  <node concept="24kQdi" id="5pu6noS9ZMz">
    <ref role="1XX52x" to="ktbj:5pu6noS5f54" resolve="Component" />
    <node concept="3EZMnI" id="5pu6noS9ZMD" role="2wV5jI">
      <node concept="l2Vlx" id="74C6il$j8MR" role="2iSdaV" />
      <node concept="3F0ifn" id="5pu6noS9ZMV" role="3EZMnx">
        <property role="3F0ifm" value="component" />
      </node>
      <node concept="3F0A7n" id="5pu6noS9ZNj" role="3EZMnx">
        <ref role="1NtTu8" to="tpck:h0TrG11" resolve="name" />
      </node>
      <node concept="3F0ifn" id="74C6il$tW9v" role="3EZMnx">
        <property role="3F0ifm" value="subsystem" />
      </node>
      <node concept="3F0A7n" id="74C6il$tWyG" role="3EZMnx">
        <ref role="1NtTu8" to="ktbj:74C6il$sxIF" resolve="subsystem" />
      </node>
      <node concept="3F0ifn" id="74C6il$jb9i" role="3EZMnx">
        <property role="3F0ifm" value="{" />
        <node concept="ljvvj" id="74C6il$jbqx" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3EZMnI" id="74C6il$jbOd" role="3EZMnx">
        <node concept="VPM3Z" id="74C6il$jbOf" role="3F10Kt">
          <property role="VOm3f" value="false" />
        </node>
        <node concept="lj46D" id="74C6il$jc5G" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="ljvvj" id="74C6il$jcL2" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="74C6il$jbOi" role="2iSdaV" />
        <node concept="3F0ifn" id="74C6il$jHdW" role="3EZMnx">
          <property role="3F0ifm" value="input ports:" />
          <node concept="ljvvj" id="74C6il$jHKd" role="3F10Kt">
            <property role="VOm3f" value="true" />
          </node>
        </node>
        <node concept="3F2HdR" id="74C6il$evNB" role="3EZMnx">
          <ref role="1NtTu8" to="ktbj:5pu6noS6Y52" resolve="in" />
          <node concept="l2Vlx" id="74C6il$gQuJ" role="2czzBx" />
          <node concept="lj46D" id="74C6il$hdV7" role="3F10Kt">
            <property role="VOm3f" value="true" />
          </node>
          <node concept="pj6Ft" id="74C6il$jHW7" role="3F10Kt">
            <property role="VOm3f" value="true" />
          </node>
        </node>
        <node concept="3F0ifn" id="74C6il$jImd" role="3EZMnx">
          <property role="3F0ifm" value="output ports:" />
          <node concept="ljvvj" id="74C6il$jIo1" role="3F10Kt">
            <property role="VOm3f" value="true" />
          </node>
        </node>
        <node concept="3F2HdR" id="74C6il$ey6x" role="3EZMnx">
          <ref role="1NtTu8" to="ktbj:5pu6noS6Y56" resolve="out" />
          <node concept="l2Vlx" id="74C6il$ik4r" role="2czzBx" />
          <node concept="lj46D" id="74C6il$hvmL" role="3F10Kt">
            <property role="VOm3f" value="true" />
          </node>
          <node concept="pj6Ft" id="74C6il$iRrd" role="3F10Kt">
            <property role="VOm3f" value="true" />
          </node>
        </node>
        <node concept="3F0ifn" id="74C6il$jJgy" role="3EZMnx">
          <property role="3F0ifm" value="dependencies:" />
          <node concept="ljvvj" id="74C6il$jJSR" role="3F10Kt">
            <property role="VOm3f" value="true" />
          </node>
        </node>
        <node concept="3F2HdR" id="5pu6noS9ZM_" role="3EZMnx">
          <ref role="1NtTu8" to="ktbj:5pu6noS5f57" resolve="dep" />
          <node concept="l2Vlx" id="74C6il$jKeS" role="2czzBx" />
          <node concept="lj46D" id="74C6il$jK4F" role="3F10Kt">
            <property role="VOm3f" value="true" />
          </node>
          <node concept="pj6Ft" id="74C6il$jKqN" role="3F10Kt">
            <property role="VOm3f" value="true" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="74C6il$jcv_" role="3EZMnx">
        <property role="3F0ifm" value="}" />
      </node>
      <node concept="pkWqt" id="6sC7QXwRnwV" role="pqm2j">
        <node concept="3clFbS" id="6sC7QXwRnwW" role="2VODD2">
          <node concept="3cpWs8" id="6sC7QXwRRgo" role="3cqZAp">
            <node concept="3cpWsn" id="6sC7QXwRRgp" role="3cpWs9">
              <property role="TrG5h" value="query" />
              <node concept="17QB3L" id="6sC7QXwRRgm" role="1tU5fm" />
              <node concept="2OqwBi" id="6sC7QXwRRgq" role="33vP2m">
                <node concept="2OqwBi" id="6sC7QXwRRgr" role="2Oq$k0">
                  <node concept="pncrf" id="6sC7QXwRRgs" role="2Oq$k0" />
                  <node concept="2Xjw5R" id="6sC7QXwRRgt" role="2OqNvi">
                    <node concept="1xMEDy" id="6sC7QXwRRgu" role="1xVPHs">
                      <node concept="chp4Y" id="6sC7QXwRRgv" role="ri$Ld">
                        <ref role="cht4Q" to="ktbj:5pu6noS52gF" resolve="ComponentSet" />
                      </node>
                    </node>
                  </node>
                </node>
                <node concept="3TrcHB" id="6sC7QXwRRgw" role="2OqNvi">
                  <ref role="3TsBF5" to="ktbj:6sC7QXwR9qu" resolve="query" />
                </node>
              </node>
            </node>
          </node>
          <node concept="3cpWs6" id="6sC7QXwRRJB" role="3cqZAp">
            <node concept="3K4zz7" id="6sC7QXwRVMh" role="3cqZAk">
              <node concept="3clFbT" id="6sC7QXwRW1f" role="3K4E3e">
                <property role="3clFbU" value="true" />
              </node>
              <node concept="2OqwBi" id="6sC7QXwRTS7" role="3K4Cdx">
                <node concept="37vLTw" id="6sC7QXwRScx" role="2Oq$k0">
                  <ref role="3cqZAo" node="6sC7QXwRRgp" resolve="query" />
                </node>
                <node concept="17RlXB" id="6sC7QXwRV3Z" role="2OqNvi" />
              </node>
              <node concept="2OqwBi" id="6sC7QXwRrm7" role="3K4GZi">
                <node concept="2OqwBi" id="6sC7QXwRqcj" role="2Oq$k0">
                  <node concept="pncrf" id="6sC7QXwRq7B" role="2Oq$k0" />
                  <node concept="3TrcHB" id="6sC7QXwRqPA" role="2OqNvi">
                    <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                  </node>
                </node>
                <node concept="liA8E" id="6sC7QXwRs8K" role="2OqNvi">
                  <ref role="37wK5l" to="wyt6:~String.contains(java.lang.CharSequence)" resolve="contains" />
                  <node concept="37vLTw" id="6sC7QXwRRgx" role="37wK5m">
                    <ref role="3cqZAo" node="6sC7QXwRRgp" resolve="query" />
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
    <node concept="3EZMnI" id="3ydhewawME$" role="6VMZX">
      <node concept="3F0ifn" id="3ydhewawMG5" role="3EZMnx">
        <property role="3F0ifm" value="position" />
      </node>
      <node concept="3EZMnI" id="3ydhewawO_b" role="3EZMnx">
        <node concept="VPM3Z" id="3ydhewawO_c" role="3F10Kt">
          <property role="VOm3f" value="false" />
        </node>
        <node concept="3F0ifn" id="3ydhewawO_d" role="3EZMnx">
          <property role="3F0ifm" value="x:" />
        </node>
        <node concept="3F0A7n" id="3ydhewawO_e" role="3EZMnx">
          <ref role="1NtTu8" to="ktbj:5pu6noS6XHd" resolve="x" />
        </node>
        <node concept="2iRfu4" id="3ydhewawO_f" role="2iSdaV" />
      </node>
      <node concept="3EZMnI" id="3ydhewawMGb" role="3EZMnx">
        <node concept="VPM3Z" id="3ydhewawMGd" role="3F10Kt">
          <property role="VOm3f" value="false" />
        </node>
        <node concept="3F0ifn" id="3ydhewawMGf" role="3EZMnx">
          <property role="3F0ifm" value="y:" />
        </node>
        <node concept="3F0A7n" id="3ydhewawMGt" role="3EZMnx">
          <ref role="1NtTu8" to="ktbj:5pu6noS6XHf" resolve="y" />
        </node>
        <node concept="2iRfu4" id="3ydhewawMGg" role="2iSdaV" />
      </node>
      <node concept="3EZMnI" id="6mo44cysHsR" role="3EZMnx">
        <node concept="VPM3Z" id="6mo44cysHsS" role="3F10Kt">
          <property role="VOm3f" value="false" />
        </node>
        <node concept="3F0ifn" id="6mo44cysHsT" role="3EZMnx">
          <property role="3F0ifm" value="width:" />
        </node>
        <node concept="3F0A7n" id="6mo44cysHsU" role="3EZMnx">
          <ref role="1NtTu8" to="ktbj:74C6il$sxI8" resolve="width" />
        </node>
        <node concept="2iRfu4" id="6mo44cysHsV" role="2iSdaV" />
      </node>
      <node concept="3EZMnI" id="6mo44cysHsW" role="3EZMnx">
        <node concept="VPM3Z" id="6mo44cysHsX" role="3F10Kt">
          <property role="VOm3f" value="false" />
        </node>
        <node concept="3F0ifn" id="6mo44cysHsY" role="3EZMnx">
          <property role="3F0ifm" value="height:" />
        </node>
        <node concept="3F0A7n" id="6mo44cysHsZ" role="3EZMnx">
          <ref role="1NtTu8" to="ktbj:74C6il$sxIf" resolve="heigh" />
        </node>
        <node concept="2iRfu4" id="6mo44cysHt0" role="2iSdaV" />
      </node>
      <node concept="2iRkQZ" id="3ydhewawMEB" role="2iSdaV" />
    </node>
  </node>
  <node concept="24kQdi" id="5pu6noS9ZNS">
    <ref role="1XX52x" to="ktbj:5pu6noS6R6w" resolve="Dependency" />
    <node concept="3EZMnI" id="5pu6noS9ZNX" role="2wV5jI">
      <node concept="2iRfu4" id="5pu6noS9ZNY" role="2iSdaV" />
      <node concept="3F0ifn" id="5pu6noS9ZNU" role="3EZMnx">
        <property role="3F0ifm" value="depends on" />
      </node>
      <node concept="1iCGBv" id="7SUlOxgA3lM" role="3EZMnx">
        <ref role="1NtTu8" to="ktbj:5pu6noS6Rpk" resolve="to" />
        <node concept="1sVBvm" id="7SUlOxgA3lN" role="1sWHZn">
          <node concept="3F0A7n" id="7SUlOxgABHe" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="tpck:h0TrG11" resolve="name" />
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="312cEu" id="54Q_haZUJXk">
    <property role="TrG5h" value="BlockView" />
    <node concept="312cEg" id="54Q_haZV7gi" role="jymVt">
      <property role="34CwA1" value="false" />
      <property role="eg7rD" value="false" />
      <property role="TrG5h" value="myCell" />
      <property role="3TUv4t" value="false" />
      <node concept="3uibUv" id="54Q_haZV7gk" role="1tU5fm">
        <ref role="3uigEE" to="d7dq:~TextCell" resolve="TextCell" />
      </node>
      <node concept="2ShNRf" id="54Q_haZV7j2" role="33vP2m">
        <node concept="1pGfFk" id="54Q_haZV7j3" role="2ShVmc">
          <ref role="37wK5l" to="d7dq:~TextCell.&lt;init&gt;()" resolve="TextCell" />
        </node>
      </node>
      <node concept="3Tm6S6" id="54Q_haZV7gm" role="1B3o_S" />
    </node>
    <node concept="3clFbW" id="54Q_haZV7g$" role="jymVt">
      <property role="DiZV1" value="false" />
      <property role="od$2w" value="false" />
      <node concept="3cqZAl" id="54Q_haZV7g_" role="3clF45" />
      <node concept="3clFbS" id="54Q_haZV7gA" role="3clF47">
        <node concept="XkiVB" id="54Q_haZV7j8" role="3cqZAp">
          <ref role="37wK5l" to="okxs:~CenterVerticalLayoutView.&lt;init&gt;(boolean)" resolve="CenterVerticalLayoutView" />
          <node concept="3clFbT" id="54Q_haZV7i4" role="37wK5m">
            <property role="3clFbU" value="false" />
          </node>
        </node>
        <node concept="3clFbF" id="54Q_haZV7gB" role="3cqZAp">
          <node concept="2OqwBi" id="54Q_haZV7gC" role="3clFbG">
            <node concept="1rXfSq" id="54Q_haZV7gD" role="2Oq$k0">
              <ref role="37wK5l" to="jqfx:~View.background()" resolve="background" />
            </node>
            <node concept="liA8E" id="54Q_haZV7gE" role="2OqNvi">
              <ref role="37wK5l" to="lgza:~WritableProperty.set(java.lang.Object)" resolve="set" />
              <node concept="10M0yZ" id="54Q_haZVouf" role="37wK5m">
                <ref role="1PxDUh" to="4rj2:~Color" resolve="Color" />
                <ref role="3cqZAo" to="4rj2:~Color.BLUE" resolve="BLUE" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3cpWs8" id="54Q_haZV7gH" role="3cqZAp">
          <node concept="3cpWsn" id="54Q_haZV7gG" role="3cpWs9">
            <property role="3TUv4t" value="false" />
            <property role="TrG5h" value="cellView" />
            <node concept="3uibUv" id="Cton7fV2Mk" role="1tU5fm">
              <ref role="3uigEE" to="d0r4:~CellView" resolve="CellView" />
            </node>
            <node concept="2ShNRf" id="54Q_haZV7jb" role="33vP2m">
              <node concept="1pGfFk" id="54Q_haZV7jc" role="2ShVmc">
                <ref role="37wK5l" to="d0r4:~CellView.&lt;init&gt;()" resolve="CellView" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="54Q_haZV7gK" role="3cqZAp">
          <node concept="2OqwBi" id="54Q_haZV7gL" role="3clFbG">
            <node concept="2OqwBi" id="54Q_haZV7jf" role="2Oq$k0">
              <node concept="37vLTw" id="54Q_haZV7je" role="2Oq$k0">
                <ref role="3cqZAo" node="54Q_haZV7gG" resolve="cellView" />
              </node>
              <node concept="liA8E" id="54Q_haZV7jg" role="2OqNvi">
                <ref role="37wK5l" to="jqfx:~View.background()" resolve="background" />
              </node>
            </node>
            <node concept="liA8E" id="54Q_haZV7gN" role="2OqNvi">
              <ref role="37wK5l" to="lgza:~WritableProperty.set(java.lang.Object)" resolve="set" />
              <node concept="10M0yZ" id="54Q_haZVoHY" role="37wK5m">
                <ref role="1PxDUh" to="4rj2:~Color" resolve="Color" />
                <ref role="3cqZAo" to="4rj2:~Color.LIGHT_BLUE" resolve="LIGHT_BLUE" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="54Q_haZV7gP" role="3cqZAp">
          <node concept="2OqwBi" id="54Q_haZV7jk" role="3clFbG">
            <node concept="37vLTw" id="54Q_haZV7jj" role="2Oq$k0">
              <ref role="3cqZAo" node="54Q_haZV7gi" resolve="myCell" />
            </node>
            <node concept="liA8E" id="54Q_haZV7jl" role="2OqNvi">
              <ref role="37wK5l" to="d7dq:~Cell.addTrait(jetbrains.jetpad.cell.trait.CellTrait)" resolve="addTrait" />
              <node concept="2YIFZM" id="54Q_haZVpfH" role="37wK5m">
                <ref role="37wK5l" to="5v25:~TextEditing.textEditing()" resolve="textEditing" />
                <ref role="1Pybhc" to="5v25:~TextEditing" resolve="TextEditing" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="54Q_haZV7gS" role="3cqZAp">
          <node concept="2OqwBi" id="54Q_haZV7jr" role="3clFbG">
            <node concept="2OqwBi" id="54Q_haZV7jp" role="2Oq$k0">
              <node concept="37vLTw" id="54Q_haZV7jo" role="2Oq$k0">
                <ref role="3cqZAo" node="54Q_haZV7gG" resolve="cellView" />
              </node>
              <node concept="2OwXpG" id="54Q_haZV7jq" role="2OqNvi">
                <ref role="2Oxat5" to="d0r4:~CellView.cell" resolve="cell" />
              </node>
            </node>
            <node concept="liA8E" id="54Q_haZV7js" role="2OqNvi">
              <ref role="37wK5l" to="lgza:~WritableProperty.set(java.lang.Object)" resolve="set" />
              <node concept="37vLTw" id="54Q_haZV7gU" role="37wK5m">
                <ref role="3cqZAo" node="54Q_haZV7gi" resolve="myCell" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="54Q_haZV7gV" role="3cqZAp">
          <node concept="2OqwBi" id="54Q_haZV7gW" role="3clFbG">
            <node concept="1rXfSq" id="54Q_haZV7gX" role="2Oq$k0">
              <ref role="37wK5l" to="jqfx:~View.children()" resolve="children" />
            </node>
            <node concept="liA8E" id="54Q_haZV7gY" role="2OqNvi">
              <ref role="37wK5l" to="33ny:~List.add(java.lang.Object)" resolve="add" />
              <node concept="37vLTw" id="54Q_haZV7gZ" role="37wK5m">
                <ref role="3cqZAo" node="54Q_haZV7gG" resolve="cellView" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3cpWs8" id="54Q_haZV7hH" role="3cqZAp">
          <node concept="3cpWsn" id="54Q_haZV7hG" role="3cpWs9">
            <property role="3TUv4t" value="false" />
            <property role="TrG5h" value="bottomRect" />
            <node concept="3uibUv" id="54Q_haZV7hI" role="1tU5fm">
              <ref role="3uigEE" to="jqfx:~RectView" resolve="RectView" />
            </node>
            <node concept="2ShNRf" id="54Q_haZV7jY" role="33vP2m">
              <node concept="1pGfFk" id="54Q_haZV7jZ" role="2ShVmc">
                <ref role="37wK5l" to="jqfx:~RectView.&lt;init&gt;()" resolve="RectView" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="54Q_haZV7hK" role="3cqZAp">
          <node concept="2OqwBi" id="54Q_haZV7hL" role="3clFbG">
            <node concept="2OqwBi" id="54Q_haZV7k2" role="2Oq$k0">
              <node concept="37vLTw" id="54Q_haZV7k1" role="2Oq$k0">
                <ref role="3cqZAo" node="54Q_haZV7hG" resolve="bottomRect" />
              </node>
              <node concept="liA8E" id="54Q_haZV7k3" role="2OqNvi">
                <ref role="37wK5l" to="jqfx:~View.background()" resolve="background" />
              </node>
            </node>
            <node concept="liA8E" id="54Q_haZV7hN" role="2OqNvi">
              <ref role="37wK5l" to="lgza:~WritableProperty.set(java.lang.Object)" resolve="set" />
              <node concept="10M0yZ" id="54Q_haZVyqo" role="37wK5m">
                <ref role="1PxDUh" to="4rj2:~Color" resolve="Color" />
                <ref role="3cqZAo" to="4rj2:~Color.GRAY" resolve="GRAY" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="54Q_haZV7hP" role="3cqZAp">
          <node concept="2OqwBi" id="54Q_haZV7hQ" role="3clFbG">
            <node concept="2OqwBi" id="54Q_haZV7k7" role="2Oq$k0">
              <node concept="37vLTw" id="54Q_haZV7k6" role="2Oq$k0">
                <ref role="3cqZAo" node="54Q_haZV7hG" resolve="bottomRect" />
              </node>
              <node concept="liA8E" id="54Q_haZV7k8" role="2OqNvi">
                <ref role="37wK5l" to="jqfx:~RectView.dimension()" resolve="dimension" />
              </node>
            </node>
            <node concept="liA8E" id="54Q_haZV7hS" role="2OqNvi">
              <ref role="37wK5l" to="lgza:~WritableProperty.set(java.lang.Object)" resolve="set" />
              <node concept="2ShNRf" id="54Q_haZV7k9" role="37wK5m">
                <node concept="1pGfFk" id="54Q_haZV7ka" role="2ShVmc">
                  <ref role="37wK5l" to="g88e:~Vector.&lt;init&gt;(int,int)" resolve="Vector" />
                  <node concept="3cmrfG" id="54Q_haZV7hU" role="37wK5m">
                    <property role="3cmrfH" value="100" />
                  </node>
                  <node concept="3cmrfG" id="54Q_haZV7hV" role="37wK5m">
                    <property role="3cmrfH" value="30" />
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="54Q_haZV7hW" role="3cqZAp">
          <node concept="2OqwBi" id="54Q_haZV7hX" role="3clFbG">
            <node concept="1rXfSq" id="54Q_haZV7hY" role="2Oq$k0">
              <ref role="37wK5l" to="jqfx:~View.children()" resolve="children" />
            </node>
            <node concept="liA8E" id="54Q_haZV7hZ" role="2OqNvi">
              <ref role="37wK5l" to="33ny:~List.add(java.lang.Object)" resolve="add" />
              <node concept="37vLTw" id="54Q_haZV7i0" role="37wK5m">
                <ref role="3cqZAo" node="54Q_haZV7hG" resolve="bottomRect" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="54Q_haZV7i1" role="3cqZAp">
          <node concept="1rXfSq" id="54Q_haZV7i2" role="3clFbG">
            <ref role="37wK5l" node="54Q_haZV7i6" resolve="initSynchronizers" />
          </node>
        </node>
      </node>
      <node concept="3Tm1VV" id="54Q_haZV7i5" role="1B3o_S" />
    </node>
    <node concept="3clFb_" id="54Q_haZV7i6" role="jymVt">
      <property role="TrG5h" value="initSynchronizers" />
      <property role="DiZV1" value="false" />
      <property role="od$2w" value="false" />
      <node concept="3clFbS" id="54Q_haZV7i7" role="3clF47">
        <node concept="3clFbF" id="54Q_haZV7i8" role="3cqZAp">
          <node concept="2OqwBi" id="54Q_haZV7i9" role="3clFbG">
            <node concept="2ShNRf" id="54Q_haZV7ia" role="2Oq$k0">
              <node concept="YeOm9" id="54Q_haZV7ib" role="2ShVmc">
                <node concept="1Y3b0j" id="54Q_haZV7ic" role="YeSDq">
                  <property role="2bfB8j" value="true" />
                  <property role="1sVAO0" value="false" />
                  <property role="1EXbeo" value="false" />
                  <ref role="1Y3XeK" to="sm7x:~Mapper" resolve="Mapper" />
                  <ref role="37wK5l" to="sm7x:~Mapper.&lt;init&gt;(java.lang.Object,java.lang.Object)" resolve="Mapper" />
                  <node concept="3Tm1VV" id="54Q_haZV7id" role="1B3o_S" />
                  <node concept="3clFb_" id="54Q_haZV7ie" role="jymVt">
                    <property role="TrG5h" value="registerSynchronizers" />
                    <property role="DiZV1" value="false" />
                    <property role="od$2w" value="false" />
                    <node concept="2AHcQZ" id="54Q_haZV7if" role="2AJF6D">
                      <ref role="2AI5Lk" to="wyt6:~Override" resolve="Override" />
                    </node>
                    <node concept="37vLTG" id="54Q_haZV7ig" role="3clF46">
                      <property role="TrG5h" value="configuration" />
                      <property role="3TUv4t" value="false" />
                      <node concept="3uibUv" id="54Q_haZV7ih" role="1tU5fm">
                        <ref role="3uigEE" to="sm7x:~Mapper$SynchronizersConfiguration" resolve="Mapper.SynchronizersConfiguration" />
                      </node>
                    </node>
                    <node concept="3clFbS" id="54Q_haZV7ii" role="3clF47">
                      <node concept="3clFbF" id="54Q_haZV7ij" role="3cqZAp">
                        <node concept="3nyPlj" id="54Q_haZV7ik" role="3clFbG">
                          <ref role="37wK5l" to="sm7x:~Mapper.registerSynchronizers(jetbrains.jetpad.mapper.Mapper$SynchronizersConfiguration)" resolve="registerSynchronizers" />
                          <node concept="37vLTw" id="54Q_haZV7il" role="37wK5m">
                            <ref role="3cqZAo" node="54Q_haZV7ig" resolve="configuration" />
                          </node>
                        </node>
                      </node>
                    </node>
                    <node concept="3Tmbuc" id="54Q_haZV7iM" role="1B3o_S" />
                    <node concept="3cqZAl" id="54Q_haZV7iN" role="3clF45" />
                  </node>
                  <node concept="Xjq3P" id="54Q_haZV7iO" role="37wK5m" />
                  <node concept="Xjq3P" id="54Q_haZV7iP" role="37wK5m" />
                  <node concept="3uibUv" id="54Q_haZVswc" role="2Ghqu4">
                    <ref role="3uigEE" node="54Q_haZUJXk" resolve="BlockView" />
                  </node>
                  <node concept="3uibUv" id="54Q_haZVtzS" role="2Ghqu4">
                    <ref role="3uigEE" node="54Q_haZUJXk" resolve="BlockView" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="liA8E" id="54Q_haZV7iS" role="2OqNvi">
              <ref role="37wK5l" to="sm7x:~Mapper.attachRoot()" resolve="attachRoot" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3Tm6S6" id="54Q_haZV7iT" role="1B3o_S" />
      <node concept="3cqZAl" id="54Q_haZV7iU" role="3clF45" />
    </node>
    <node concept="3clFb_" id="54Q_haZV7iV" role="jymVt">
      <property role="TrG5h" value="text" />
      <property role="DiZV1" value="false" />
      <property role="od$2w" value="false" />
      <node concept="3clFbS" id="54Q_haZV7iW" role="3clF47">
        <node concept="3cpWs6" id="54Q_haZV7iX" role="3cqZAp">
          <node concept="2OqwBi" id="54Q_haZV7kR" role="3cqZAk">
            <node concept="37vLTw" id="54Q_haZV7kQ" role="2Oq$k0">
              <ref role="3cqZAo" node="54Q_haZV7gi" resolve="myCell" />
            </node>
            <node concept="liA8E" id="54Q_haZV7kS" role="2OqNvi">
              <ref role="37wK5l" to="d7dq:~TextCell.text()" resolve="text" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3Tm1VV" id="54Q_haZV7iZ" role="1B3o_S" />
      <node concept="3uibUv" id="54Q_haZV7j0" role="3clF45">
        <ref role="3uigEE" to="lgza:~Property" resolve="Property" />
        <node concept="3uibUv" id="54Q_haZV7j1" role="11_B2D">
          <ref role="3uigEE" to="wyt6:~String" resolve="String" />
        </node>
      </node>
      <node concept="zeN4a" id="54Q_haZVKaU" role="lGtFl" />
    </node>
    <node concept="3Tm1VV" id="54Q_haZUJXl" role="1B3o_S" />
    <node concept="3uibUv" id="2CIEV4acNGo" role="1zkMxy">
      <ref role="3uigEE" to="okxs:~CenterVerticalLayoutView" resolve="CenterVerticalLayoutView" />
    </node>
    <node concept="3FP93d" id="54Q_haZVHoB" role="lGtFl" />
    <node concept="3uibUv" id="7SUlOxgwBr1" role="EKbjA">
      <ref role="3uigEE" to="8n5u:70DU5_aRQ79" resolve="MovableContentView" />
    </node>
  </node>
  <node concept="24kQdi" id="54Q_haZZ5IS">
    <property role="3GE5qa" value="" />
    <ref role="1XX52x" to="ktbj:5pu6noS6Y5A" resolve="InPort" />
    <node concept="3F0A7n" id="74C6il$gx0J" role="2wV5jI">
      <ref role="1NtTu8" to="tpck:h0TrG11" resolve="name" />
    </node>
  </node>
  <node concept="24kQdi" id="54Q_haZZ5IX">
    <property role="3GE5qa" value="" />
    <ref role="1XX52x" to="ktbj:5pu6noS6Y55" resolve="OutPort" />
    <node concept="3F0A7n" id="74C6il$gxaH" role="2wV5jI">
      <ref role="1NtTu8" to="tpck:h0TrG11" resolve="name" />
    </node>
  </node>
  <node concept="24kQdi" id="54Q_hb054Dm">
    <ref role="1XX52x" to="ktbj:5pu6noS52gF" resolve="ComponentSet" />
    <node concept="1CiYdB" id="54Q_hb05568" role="2wV5jI">
      <node concept="2XI2dN" id="54Q_hb0556a" role="2XI0mt">
        <node concept="3clFbS" id="54Q_hb0556c" role="2VODD2">
          <node concept="3clFbF" id="54Q_hb056Hp" role="3cqZAp">
            <node concept="2ShNRf" id="54Q_hb056Hn" role="3clFbG">
              <node concept="YeOm9" id="54Q_hb057TV" role="2ShVmc">
                <node concept="1Y3b0j" id="54Q_hb057TY" role="YeSDq">
                  <property role="2bfB8j" value="true" />
                  <ref role="1Y3XeK" to="squ6:3ThmjU3UlMw" resolve="TableModel" />
                  <ref role="37wK5l" to="wyt6:~Object.&lt;init&gt;()" resolve="Object" />
                  <node concept="3Tm1VV" id="54Q_hb057TZ" role="1B3o_S" />
                  <node concept="3clFb_" id="54Q_hb057U0" role="jymVt">
                    <property role="1EzhhJ" value="false" />
                    <property role="TrG5h" value="getColumnCount" />
                    <node concept="3Tm1VV" id="54Q_hb057U1" role="1B3o_S" />
                    <node concept="10Oyi0" id="54Q_hb057U2" role="3clF45" />
                    <node concept="3clFbS" id="54Q_hb057U4" role="3clF47">
                      <node concept="3clFbF" id="54Q_hb0592a" role="3cqZAp">
                        <node concept="3cpWs3" id="7FiYmJ2ZrQs" role="3clFbG">
                          <node concept="3cmrfG" id="7FiYmJ2ZrQC" role="3uHU7w">
                            <property role="3cmrfH" value="1" />
                          </node>
                          <node concept="2OqwBi" id="54Q_hb05adR" role="3uHU7B">
                            <node concept="2OqwBi" id="54Q_hb05942" role="2Oq$k0">
                              <node concept="pncrf" id="54Q_hb05929" role="2Oq$k0" />
                              <node concept="3Tsc0h" id="54Q_hb059eg" role="2OqNvi">
                                <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
                              </node>
                            </node>
                            <node concept="liA8E" id="54Q_hb05ebG" role="2OqNvi">
                              <ref role="37wK5l" to="33ny:~List.size()" resolve="size" />
                            </node>
                          </node>
                        </node>
                      </node>
                    </node>
                  </node>
                  <node concept="3clFb_" id="54Q_hb057U6" role="jymVt">
                    <property role="1EzhhJ" value="false" />
                    <property role="TrG5h" value="getRowCount" />
                    <node concept="10Oyi0" id="54Q_hb057U7" role="3clF45" />
                    <node concept="3Tm1VV" id="54Q_hb057U9" role="1B3o_S" />
                    <node concept="3clFbS" id="54Q_hb057Ua" role="3clF47">
                      <node concept="3clFbF" id="54Q_hb05e_W" role="3cqZAp">
                        <node concept="3cpWs3" id="7FiYmJ2ZspB" role="3clFbG">
                          <node concept="3cmrfG" id="7FiYmJ2ZspN" role="3uHU7w">
                            <property role="3cmrfH" value="1" />
                          </node>
                          <node concept="2OqwBi" id="54Q_hb05e_X" role="3uHU7B">
                            <node concept="2OqwBi" id="54Q_hb05e_Y" role="2Oq$k0">
                              <node concept="pncrf" id="54Q_hb05e_Z" role="2Oq$k0" />
                              <node concept="3Tsc0h" id="54Q_hb05eA0" role="2OqNvi">
                                <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
                              </node>
                            </node>
                            <node concept="liA8E" id="54Q_hb05eA1" role="2OqNvi">
                              <ref role="37wK5l" to="33ny:~List.size()" resolve="size" />
                            </node>
                          </node>
                        </node>
                      </node>
                    </node>
                  </node>
                  <node concept="3clFb_" id="54Q_hb057Uc" role="jymVt">
                    <property role="1EzhhJ" value="false" />
                    <property role="TrG5h" value="deleteRow" />
                    <node concept="37vLTG" id="54Q_hb057Ue" role="3clF46">
                      <property role="TrG5h" value="rowNumber" />
                      <node concept="10Oyi0" id="54Q_hb057Uf" role="1tU5fm" />
                    </node>
                    <node concept="3Tm1VV" id="54Q_hb057Ug" role="1B3o_S" />
                    <node concept="3cqZAl" id="54Q_hb057Uh" role="3clF45" />
                    <node concept="3clFbS" id="54Q_hb057Ui" role="3clF47" />
                  </node>
                  <node concept="3clFb_" id="54Q_hb057Uk" role="jymVt">
                    <property role="1EzhhJ" value="false" />
                    <property role="TrG5h" value="getValueAt" />
                    <node concept="3Tm1VV" id="54Q_hb057Ul" role="1B3o_S" />
                    <node concept="3Tqbb2" id="54Q_hb057Un" role="3clF45" />
                    <node concept="37vLTG" id="54Q_hb057Uo" role="3clF46">
                      <property role="TrG5h" value="row" />
                      <node concept="10Oyi0" id="54Q_hb057Up" role="1tU5fm" />
                    </node>
                    <node concept="37vLTG" id="54Q_hb057Uq" role="3clF46">
                      <property role="TrG5h" value="column" />
                      <node concept="10Oyi0" id="54Q_hb057Ur" role="1tU5fm" />
                    </node>
                    <node concept="3clFbS" id="54Q_hb057Us" role="3clF47">
                      <node concept="3clFbJ" id="7FiYmJ2ZunZ" role="3cqZAp">
                        <node concept="3clFbS" id="7FiYmJ2Zuo2" role="3clFbx">
                          <node concept="3cpWs6" id="U5sb5SK8cH" role="3cqZAp">
                            <node concept="10Nm6u" id="U5sb5SK973" role="3cqZAk" />
                          </node>
                        </node>
                        <node concept="1Wc70l" id="U5sb5SK2O4" role="3clFbw">
                          <node concept="3clFbC" id="U5sb5SK2yj" role="3uHU7w">
                            <node concept="3cmrfG" id="U5sb5SK2yk" role="3uHU7w">
                              <property role="3cmrfH" value="0" />
                            </node>
                            <node concept="37vLTw" id="U5sb5SK2yl" role="3uHU7B">
                              <ref role="3cqZAo" node="54Q_hb057Uq" resolve="column" />
                            </node>
                          </node>
                          <node concept="3clFbC" id="U5sb5SK2ym" role="3uHU7B">
                            <node concept="37vLTw" id="U5sb5SK2yn" role="3uHU7B">
                              <ref role="3cqZAo" node="54Q_hb057Uo" resolve="row" />
                            </node>
                            <node concept="3cmrfG" id="U5sb5SK2yo" role="3uHU7w">
                              <property role="3cmrfH" value="0" />
                            </node>
                          </node>
                        </node>
                      </node>
                      <node concept="3clFbJ" id="U5sb5SKclA" role="3cqZAp">
                        <node concept="3clFbS" id="U5sb5SKclD" role="3clFbx">
                          <node concept="3cpWs6" id="7FiYmJ2Zwk0" role="3cqZAp">
                            <node concept="2OqwBi" id="Hrb9mBKiKD" role="3cqZAk">
                              <node concept="2OqwBi" id="U5sb5SKhov" role="2Oq$k0">
                                <node concept="2OqwBi" id="7FiYmJ2ZzvT" role="2Oq$k0">
                                  <node concept="2OqwBi" id="7FiYmJ2ZxgX" role="2Oq$k0">
                                    <node concept="pncrf" id="7FiYmJ2Zx4$" role="2Oq$k0" />
                                    <node concept="3Tsc0h" id="7FiYmJ2ZxKt" role="2OqNvi">
                                      <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
                                    </node>
                                  </node>
                                  <node concept="34jXtK" id="7FiYmJ2ZAQ_" role="2OqNvi">
                                    <node concept="3cpWsd" id="7FiYmJ30ggF" role="25WWJ7">
                                      <node concept="3cmrfG" id="7FiYmJ30ggR" role="3uHU7w">
                                        <property role="3cmrfH" value="1" />
                                      </node>
                                      <node concept="37vLTw" id="7FiYmJ2ZCF3" role="3uHU7B">
                                        <ref role="3cqZAo" node="54Q_hb057Uq" resolve="column" />
                                      </node>
                                    </node>
                                  </node>
                                </node>
                                <node concept="3Tsc0h" id="Hrb9mBKgJL" role="2OqNvi">
                                  <ref role="3TtcxE" to="ktbj:5pu6noS6Y52" resolve="in" />
                                </node>
                              </node>
                              <node concept="1uHKPH" id="Hrb9mBKlMU" role="2OqNvi" />
                            </node>
                          </node>
                        </node>
                        <node concept="3clFbC" id="U5sb5SKdFf" role="3clFbw">
                          <node concept="3cmrfG" id="U5sb5SKdPF" role="3uHU7w">
                            <property role="3cmrfH" value="0" />
                          </node>
                          <node concept="37vLTw" id="U5sb5SKdgz" role="3uHU7B">
                            <ref role="3cqZAo" node="54Q_hb057Uo" resolve="row" />
                          </node>
                        </node>
                      </node>
                      <node concept="3clFbJ" id="U5sb5SKj$8" role="3cqZAp">
                        <node concept="3clFbS" id="U5sb5SKj$9" role="3clFbx">
                          <node concept="3cpWs8" id="TiIH7h1NrF" role="3cqZAp">
                            <node concept="3cpWsn" id="TiIH7h1NrG" role="3cpWs9">
                              <property role="TrG5h" value="component" />
                              <node concept="3Tqbb2" id="TiIH7h1NrA" role="1tU5fm">
                                <ref role="ehGHo" to="ktbj:5pu6noS5f54" resolve="Component" />
                              </node>
                              <node concept="2OqwBi" id="TiIH7h1NrH" role="33vP2m">
                                <node concept="2OqwBi" id="TiIH7h1NrI" role="2Oq$k0">
                                  <node concept="pncrf" id="TiIH7h1NrJ" role="2Oq$k0" />
                                  <node concept="3Tsc0h" id="TiIH7h1NrK" role="2OqNvi">
                                    <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
                                  </node>
                                </node>
                                <node concept="34jXtK" id="TiIH7h1NrL" role="2OqNvi">
                                  <node concept="3cpWsd" id="TiIH7h1NrM" role="25WWJ7">
                                    <node concept="3cmrfG" id="TiIH7h1NrN" role="3uHU7w">
                                      <property role="3cmrfH" value="1" />
                                    </node>
                                    <node concept="37vLTw" id="TiIH7h1NrO" role="3uHU7B">
                                      <ref role="3cqZAo" node="54Q_hb057Uo" resolve="row" />
                                    </node>
                                  </node>
                                </node>
                              </node>
                            </node>
                          </node>
                          <node concept="3clFbJ" id="TiIH7h1ONp" role="3cqZAp">
                            <node concept="3clFbS" id="TiIH7h1ONs" role="3clFbx">
                              <node concept="3cpWs6" id="TiIH7h1TjR" role="3cqZAp">
                                <node concept="37vLTw" id="TiIH7h1TrH" role="3cqZAk">
                                  <ref role="3cqZAo" node="TiIH7h1NrG" resolve="component" />
                                </node>
                              </node>
                            </node>
                            <node concept="2OqwBi" id="TiIH7h1QFx" role="3clFbw">
                              <node concept="2OqwBi" id="TiIH7h1Pw5" role="2Oq$k0">
                                <node concept="37vLTw" id="TiIH7h1P9d" role="2Oq$k0">
                                  <ref role="3cqZAo" node="TiIH7h1NrG" resolve="component" />
                                </node>
                                <node concept="3Tsc0h" id="TiIH7h1PEX" role="2OqNvi">
                                  <ref role="3TtcxE" to="ktbj:5pu6noS6Y56" resolve="out" />
                                </node>
                              </node>
                              <node concept="1v1jN8" id="TiIH7h1ThH" role="2OqNvi" />
                            </node>
                          </node>
                          <node concept="3cpWs6" id="U5sb5SKj$a" role="3cqZAp">
                            <node concept="2OqwBi" id="Hrb9mBKqaf" role="3cqZAk">
                              <node concept="2OqwBi" id="U5sb5SKj$b" role="2Oq$k0">
                                <node concept="37vLTw" id="TiIH7h1NrP" role="2Oq$k0">
                                  <ref role="3cqZAo" node="TiIH7h1NrG" resolve="component" />
                                </node>
                                <node concept="3Tsc0h" id="Hrb9mBKorB" role="2OqNvi">
                                  <ref role="3TtcxE" to="ktbj:5pu6noS6Y56" resolve="out" />
                                </node>
                              </node>
                              <node concept="1uHKPH" id="Hrb9mBKrE9" role="2OqNvi" />
                            </node>
                          </node>
                        </node>
                        <node concept="3clFbC" id="U5sb5SKj$l" role="3clFbw">
                          <node concept="3cmrfG" id="U5sb5SKj$m" role="3uHU7w">
                            <property role="3cmrfH" value="0" />
                          </node>
                          <node concept="37vLTw" id="U5sb5SKkqi" role="3uHU7B">
                            <ref role="3cqZAo" node="54Q_hb057Uq" resolve="column" />
                          </node>
                        </node>
                      </node>
                      <node concept="3clFbF" id="54Q_hb05eHg" role="3cqZAp">
                        <node concept="2OqwBi" id="54Q_hb05qzO" role="3clFbG">
                          <node concept="2OqwBi" id="54Q_hb05jOU" role="2Oq$k0">
                            <node concept="2OqwBi" id="54Q_hb05fUg" role="2Oq$k0">
                              <node concept="2OqwBi" id="54Q_hb05eJs" role="2Oq$k0">
                                <node concept="pncrf" id="54Q_hb05eHf" role="2Oq$k0" />
                                <node concept="3Tsc0h" id="54Q_hb05eTA" role="2OqNvi">
                                  <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
                                </node>
                              </node>
                              <node concept="34jXtK" id="54Q_hb05ouJ" role="2OqNvi">
                                <node concept="3cpWsd" id="7FiYmJ2ZsWV" role="25WWJ7">
                                  <node concept="3cmrfG" id="7FiYmJ2ZsX7" role="3uHU7w">
                                    <property role="3cmrfH" value="1" />
                                  </node>
                                  <node concept="37vLTw" id="54Q_hb05oyJ" role="3uHU7B">
                                    <ref role="3cqZAo" node="54Q_hb057Uo" resolve="row" />
                                  </node>
                                </node>
                              </node>
                            </node>
                            <node concept="3Tsc0h" id="54Q_hb05prG" role="2OqNvi">
                              <ref role="3TtcxE" to="ktbj:5pu6noS5f57" resolve="dep" />
                            </node>
                          </node>
                          <node concept="1z4cxt" id="U5sb5SKmVA" role="2OqNvi">
                            <node concept="1bVj0M" id="U5sb5SKmVC" role="23t8la">
                              <node concept="3clFbS" id="U5sb5SKmVD" role="1bW5cS">
                                <node concept="3clFbF" id="U5sb5SKmVE" role="3cqZAp">
                                  <node concept="3clFbC" id="U5sb5SKmVF" role="3clFbG">
                                    <node concept="2OqwBi" id="U5sb5SKmVG" role="3uHU7w">
                                      <node concept="2OqwBi" id="U5sb5SKmVH" role="2Oq$k0">
                                        <node concept="pncrf" id="U5sb5SKmVI" role="2Oq$k0" />
                                        <node concept="3Tsc0h" id="U5sb5SKmVJ" role="2OqNvi">
                                          <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
                                        </node>
                                      </node>
                                      <node concept="34jXtK" id="U5sb5SKmVK" role="2OqNvi">
                                        <node concept="3cpWsd" id="U5sb5SKmVL" role="25WWJ7">
                                          <node concept="3cmrfG" id="U5sb5SKmVM" role="3uHU7w">
                                            <property role="3cmrfH" value="1" />
                                          </node>
                                          <node concept="37vLTw" id="U5sb5SKmVN" role="3uHU7B">
                                            <ref role="3cqZAo" node="54Q_hb057Uq" resolve="column" />
                                          </node>
                                        </node>
                                      </node>
                                    </node>
                                    <node concept="2OqwBi" id="U5sb5SKmVO" role="3uHU7B">
                                      <node concept="37vLTw" id="U5sb5SKmVP" role="2Oq$k0">
                                        <ref role="3cqZAo" node="5W7E4fV0WXF" resolve="it" />
                                      </node>
                                      <node concept="3TrEf2" id="U5sb5SKmVQ" role="2OqNvi">
                                        <ref role="3Tt5mk" to="ktbj:5pu6noS6Rpk" resolve="to" />
                                      </node>
                                    </node>
                                  </node>
                                </node>
                              </node>
                              <node concept="gl6BB" id="5W7E4fV0WXF" role="1bW2Oz">
                                <property role="TrG5h" value="it" />
                                <node concept="2jxLKc" id="5W7E4fV0WXG" role="1tU5fm" />
                              </node>
                            </node>
                          </node>
                        </node>
                      </node>
                    </node>
                  </node>
                  <node concept="3clFb_" id="54Q_hb057Uu" role="jymVt">
                    <property role="1EzhhJ" value="false" />
                    <property role="TrG5h" value="createElement" />
                    <node concept="37vLTG" id="54Q_hb057Uv" role="3clF46">
                      <property role="TrG5h" value="row" />
                      <node concept="10Oyi0" id="54Q_hb057Uw" role="1tU5fm" />
                    </node>
                    <node concept="3Tm1VV" id="54Q_hb057Uy" role="1B3o_S" />
                    <node concept="3cqZAl" id="54Q_hb057Uz" role="3clF45" />
                    <node concept="37vLTG" id="54Q_hb057U$" role="3clF46">
                      <property role="TrG5h" value="column" />
                      <node concept="10Oyi0" id="54Q_hb057U_" role="1tU5fm" />
                    </node>
                    <node concept="3clFbS" id="54Q_hb057UA" role="3clF47" />
                  </node>
                  <node concept="3clFb_" id="54Q_hb057UC" role="jymVt">
                    <property role="1EzhhJ" value="false" />
                    <property role="TrG5h" value="getSubstituteInfo" />
                    <node concept="3uibUv" id="54Q_hb057UD" role="3clF45">
                      <ref role="3uigEE" to="f4zo:~SubstituteInfo" resolve="SubstituteInfo" />
                    </node>
                    <node concept="37vLTG" id="54Q_hb057UE" role="3clF46">
                      <property role="TrG5h" value="row" />
                      <node concept="10Oyi0" id="54Q_hb057UF" role="1tU5fm" />
                    </node>
                    <node concept="3Tm1VV" id="54Q_hb057UG" role="1B3o_S" />
                    <node concept="37vLTG" id="54Q_hb057UI" role="3clF46">
                      <property role="TrG5h" value="column" />
                      <node concept="10Oyi0" id="54Q_hb057UJ" role="1tU5fm" />
                    </node>
                    <node concept="3clFbS" id="54Q_hb057UK" role="3clF47">
                      <node concept="3cpWs6" id="54Q_hb05TNu" role="3cqZAp">
                        <node concept="2ShNRf" id="54Q_hb05U3c" role="3cqZAk">
                          <node concept="YeOm9" id="54Q_hb05Vaw" role="2ShVmc">
                            <node concept="1Y3b0j" id="54Q_hb05Vaz" role="YeSDq">
                              <property role="2bfB8j" value="true" />
                              <ref role="1Y3XeK" to="f4zo:~SubstituteInfo" resolve="SubstituteInfo" />
                              <ref role="37wK5l" to="wyt6:~Object.&lt;init&gt;()" resolve="Object" />
                              <node concept="3Tm1VV" id="54Q_hb05Va$" role="1B3o_S" />
                              <node concept="3clFb_" id="54Q_hb05Va_" role="jymVt">
                                <property role="1EzhhJ" value="false" />
                                <property role="TrG5h" value="getMatchingActions" />
                                <property role="DiZV1" value="false" />
                                <node concept="3Tm1VV" id="54Q_hb05VaA" role="1B3o_S" />
                                <node concept="3uibUv" id="54Q_hb05VaC" role="3clF45">
                                  <ref role="3uigEE" to="33ny:~List" resolve="List" />
                                  <node concept="3uibUv" id="54Q_hb05VaD" role="11_B2D">
                                    <ref role="3uigEE" to="f4zo:~SubstituteAction" resolve="SubstituteAction" />
                                  </node>
                                </node>
                                <node concept="37vLTG" id="54Q_hb05VaE" role="3clF46">
                                  <property role="TrG5h" value="p0" />
                                  <node concept="3uibUv" id="54Q_hb05VaF" role="1tU5fm">
                                    <ref role="3uigEE" to="wyt6:~String" resolve="String" />
                                  </node>
                                </node>
                                <node concept="37vLTG" id="54Q_hb05VaG" role="3clF46">
                                  <property role="TrG5h" value="p1" />
                                  <node concept="10P_77" id="54Q_hb05VaH" role="1tU5fm" />
                                </node>
                                <node concept="3clFbS" id="54Q_hb05VaI" role="3clF47">
                                  <node concept="3cpWs6" id="54Q_hb060Yg" role="3cqZAp">
                                    <node concept="2ShNRf" id="U5sb5SL7Sw" role="3cqZAk">
                                      <node concept="1pGfFk" id="U5sb5SL7Sx" role="2ShVmc">
                                        <ref role="37wK5l" to="33ny:~ArrayList.&lt;init&gt;()" resolve="ArrayList" />
                                        <node concept="3uibUv" id="U5sb5SL7Sy" role="1pMfVU">
                                          <ref role="3uigEE" to="f4zo:~SubstituteAction" resolve="SubstituteAction" />
                                        </node>
                                      </node>
                                    </node>
                                  </node>
                                </node>
                              </node>
                              <node concept="3clFb_" id="54Q_hb05VaK" role="jymVt">
                                <property role="1EzhhJ" value="false" />
                                <property role="TrG5h" value="getSmartMatchingActions" />
                                <property role="DiZV1" value="false" />
                                <node concept="3Tm1VV" id="54Q_hb05VaL" role="1B3o_S" />
                                <node concept="3uibUv" id="54Q_hb05VaN" role="3clF45">
                                  <ref role="3uigEE" to="33ny:~List" resolve="List" />
                                  <node concept="3uibUv" id="54Q_hb05VaO" role="11_B2D">
                                    <ref role="3uigEE" to="f4zo:~SubstituteAction" resolve="SubstituteAction" />
                                  </node>
                                </node>
                                <node concept="37vLTG" id="54Q_hb05VaP" role="3clF46">
                                  <property role="TrG5h" value="p0" />
                                  <node concept="3uibUv" id="54Q_hb05VaQ" role="1tU5fm">
                                    <ref role="3uigEE" to="wyt6:~String" resolve="String" />
                                  </node>
                                </node>
                                <node concept="37vLTG" id="54Q_hb05VaR" role="3clF46">
                                  <property role="TrG5h" value="p1" />
                                  <node concept="10P_77" id="54Q_hb05VaS" role="1tU5fm" />
                                </node>
                                <node concept="37vLTG" id="54Q_hb05VaT" role="3clF46">
                                  <property role="TrG5h" value="p2" />
                                  <node concept="3uibUv" id="54Q_hb05VaU" role="1tU5fm">
                                    <ref role="3uigEE" to="f4zo:~EditorCell" resolve="EditorCell" />
                                  </node>
                                </node>
                                <node concept="3clFbS" id="54Q_hb05VaV" role="3clF47">
                                  <node concept="3cpWs6" id="54Q_hb0631v" role="3cqZAp">
                                    <node concept="2ShNRf" id="U5sb5SKZ3t" role="3cqZAk">
                                      <node concept="1pGfFk" id="U5sb5SL48G" role="2ShVmc">
                                        <ref role="37wK5l" to="33ny:~ArrayList.&lt;init&gt;()" resolve="ArrayList" />
                                        <node concept="3uibUv" id="U5sb5SL5Gd" role="1pMfVU">
                                          <ref role="3uigEE" to="f4zo:~SubstituteAction" resolve="SubstituteAction" />
                                        </node>
                                      </node>
                                    </node>
                                  </node>
                                </node>
                              </node>
                              <node concept="3clFb_" id="54Q_hb05VaX" role="jymVt">
                                <property role="1EzhhJ" value="false" />
                                <property role="TrG5h" value="invalidateActions" />
                                <property role="DiZV1" value="false" />
                                <node concept="3Tm1VV" id="54Q_hb05VaY" role="1B3o_S" />
                                <node concept="3cqZAl" id="54Q_hb05Vb0" role="3clF45" />
                                <node concept="3clFbS" id="54Q_hb05Vb1" role="3clF47" />
                              </node>
                              <node concept="3clFb_" id="54Q_hb05Vb3" role="jymVt">
                                <property role="1EzhhJ" value="false" />
                                <property role="TrG5h" value="setOriginalText" />
                                <property role="DiZV1" value="false" />
                                <node concept="3Tm1VV" id="54Q_hb05Vb4" role="1B3o_S" />
                                <node concept="3cqZAl" id="54Q_hb05Vb6" role="3clF45" />
                                <node concept="37vLTG" id="54Q_hb05Vb7" role="3clF46">
                                  <property role="TrG5h" value="p0" />
                                  <node concept="3uibUv" id="54Q_hb05Vb8" role="1tU5fm">
                                    <ref role="3uigEE" to="wyt6:~String" resolve="String" />
                                  </node>
                                </node>
                                <node concept="3clFbS" id="54Q_hb05Vb9" role="3clF47" />
                              </node>
                              <node concept="3clFb_" id="54Q_hb05Vbb" role="jymVt">
                                <property role="1EzhhJ" value="false" />
                                <property role="TrG5h" value="getOriginalText" />
                                <property role="DiZV1" value="false" />
                                <node concept="3Tm1VV" id="54Q_hb05Vbc" role="1B3o_S" />
                                <node concept="3uibUv" id="54Q_hb05Vbe" role="3clF45">
                                  <ref role="3uigEE" to="wyt6:~String" resolve="String" />
                                </node>
                                <node concept="3clFbS" id="54Q_hb05Vbf" role="3clF47">
                                  <node concept="3cpWs6" id="54Q_hb0633D" role="3cqZAp">
                                    <node concept="Xl_RD" id="54Q_hb063lb" role="3cqZAk">
                                      <property role="Xl_RC" value="" />
                                    </node>
                                  </node>
                                </node>
                              </node>
                              <node concept="3clFb_" id="54Q_hb05Vbh" role="jymVt">
                                <property role="1EzhhJ" value="false" />
                                <property role="TrG5h" value="hasExactlyNActions" />
                                <property role="DiZV1" value="false" />
                                <node concept="3Tm1VV" id="54Q_hb05Vbi" role="1B3o_S" />
                                <node concept="10P_77" id="54Q_hb05Vbk" role="3clF45" />
                                <node concept="37vLTG" id="54Q_hb05Vbl" role="3clF46">
                                  <property role="TrG5h" value="p0" />
                                  <node concept="3uibUv" id="54Q_hb05Vbm" role="1tU5fm">
                                    <ref role="3uigEE" to="wyt6:~String" resolve="String" />
                                  </node>
                                </node>
                                <node concept="37vLTG" id="54Q_hb05Vbn" role="3clF46">
                                  <property role="TrG5h" value="p1" />
                                  <node concept="10P_77" id="54Q_hb05Vbo" role="1tU5fm" />
                                </node>
                                <node concept="37vLTG" id="54Q_hb05Vbp" role="3clF46">
                                  <property role="TrG5h" value="p2" />
                                  <node concept="10Oyi0" id="54Q_hb05Vbq" role="1tU5fm" />
                                </node>
                                <node concept="3clFbS" id="54Q_hb05Vbr" role="3clF47">
                                  <node concept="3cpWs6" id="54Q_hb0640K" role="3cqZAp">
                                    <node concept="3clFbT" id="54Q_hb064Gq" role="3cqZAk">
                                      <property role="3clFbU" value="false" />
                                    </node>
                                  </node>
                                </node>
                              </node>
                            </node>
                          </node>
                        </node>
                      </node>
                    </node>
                  </node>
                  <node concept="3clFb_" id="54Q_hb057UM" role="jymVt">
                    <property role="1EzhhJ" value="false" />
                    <property role="TrG5h" value="insertRow" />
                    <node concept="37vLTG" id="54Q_hb057UN" role="3clF46">
                      <property role="TrG5h" value="rowNumber" />
                      <node concept="10Oyi0" id="54Q_hb057UO" role="1tU5fm" />
                    </node>
                    <node concept="3cqZAl" id="54Q_hb057UP" role="3clF45" />
                    <node concept="3Tm1VV" id="54Q_hb057UR" role="1B3o_S" />
                    <node concept="3clFbS" id="54Q_hb057US" role="3clF47" />
                  </node>
                  <node concept="3clFb_" id="54Q_hb057UU" role="jymVt">
                    <property role="1EzhhJ" value="false" />
                    <property role="TrG5h" value="deleteColumn" />
                    <node concept="37vLTG" id="54Q_hb057UV" role="3clF46">
                      <property role="TrG5h" value="columnNumber" />
                      <node concept="10Oyi0" id="54Q_hb057UW" role="1tU5fm" />
                    </node>
                    <node concept="3cqZAl" id="54Q_hb057UX" role="3clF45" />
                    <node concept="3Tm1VV" id="54Q_hb057UZ" role="1B3o_S" />
                    <node concept="3clFbS" id="54Q_hb057V0" role="3clF47" />
                  </node>
                  <node concept="3clFb_" id="54Q_hb057V2" role="jymVt">
                    <property role="1EzhhJ" value="false" />
                    <property role="TrG5h" value="insertColumn" />
                    <node concept="37vLTG" id="54Q_hb057V3" role="3clF46">
                      <property role="TrG5h" value="columnNumber" />
                      <node concept="10Oyi0" id="54Q_hb057V4" role="1tU5fm" />
                    </node>
                    <node concept="3cqZAl" id="54Q_hb057V5" role="3clF45" />
                    <node concept="3Tm1VV" id="54Q_hb057V7" role="1B3o_S" />
                    <node concept="3clFbS" id="54Q_hb057V8" role="3clF47" />
                  </node>
                  <node concept="3clFb_" id="54Q_hb057Va" role="jymVt">
                    <property role="1EzhhJ" value="false" />
                    <property role="TrG5h" value="getMaxColumnWidth" />
                    <node concept="37vLTG" id="54Q_hb057Vb" role="3clF46">
                      <property role="TrG5h" value="columnNumber" />
                      <node concept="10Oyi0" id="54Q_hb057Vc" role="1tU5fm" />
                    </node>
                    <node concept="10Oyi0" id="54Q_hb057Vd" role="3clF45" />
                    <node concept="3Tm1VV" id="54Q_hb057Vf" role="1B3o_S" />
                    <node concept="3clFbS" id="54Q_hb057Vg" role="3clF47">
                      <node concept="3clFbF" id="54Q_hb071zq" role="3cqZAp">
                        <node concept="3K4zz7" id="54Q_hb0737i" role="3clFbG">
                          <node concept="3cmrfG" id="54Q_hb073he" role="3K4E3e">
                            <property role="3cmrfH" value="100" />
                          </node>
                          <node concept="3cmrfG" id="54Q_hb073hZ" role="3K4GZi">
                            <property role="3cmrfH" value="20" />
                          </node>
                          <node concept="3clFbC" id="54Q_hb072us" role="3K4Cdx">
                            <node concept="3cmrfG" id="54Q_hb072H3" role="3uHU7w">
                              <property role="3cmrfH" value="0" />
                            </node>
                            <node concept="37vLTw" id="54Q_hb071zp" role="3uHU7B">
                              <ref role="3cqZAo" node="54Q_hb057Vb" resolve="columnNumber" />
                            </node>
                          </node>
                        </node>
                      </node>
                    </node>
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
    <node concept="2aJ2om" id="54Q_hb0553F" role="CpUAK">
      <ref role="2$4xQ3" node="54Q_hb054Do" resolve="table" />
    </node>
  </node>
  <node concept="24kQdi" id="7FiYmJ2ZDCs">
    <ref role="1XX52x" to="ktbj:5pu6noS5f54" resolve="Component" />
    <node concept="3F0A7n" id="7FiYmJ2ZDCw" role="2wV5jI">
      <ref role="1NtTu8" to="tpck:h0TrG11" resolve="name" />
    </node>
    <node concept="2aJ2om" id="7FiYmJ2ZDCu" role="CpUAK">
      <ref role="2$4xQ3" node="54Q_hb054Do" resolve="table" />
    </node>
  </node>
  <node concept="1h_SRR" id="6sC7QXwUVIu">
    <property role="TrG5h" value="delComponent" />
    <ref role="1h_SK9" to="ktbj:5pu6noS5f54" resolve="Component" />
    <node concept="1hA7zw" id="6sC7QXwUWhW" role="1h_SK8">
      <property role="1hAc7j" value="g_hAxAO/delete_action_id" />
      <node concept="1hAIg9" id="6sC7QXwUWhX" role="1hA7z_">
        <node concept="3clFbS" id="6sC7QXwUWhY" role="2VODD2">
          <node concept="3cpWs8" id="6sC7QXwVa_n" role="3cqZAp">
            <node concept="3cpWsn" id="6sC7QXwVa_o" role="3cpWs9">
              <property role="TrG5h" value="list" />
              <node concept="_YKpA" id="6sC7QXwVazI" role="1tU5fm">
                <node concept="3Tqbb2" id="6sC7QXwVazL" role="_ZDj9">
                  <ref role="ehGHo" to="ktbj:5pu6noS6R6w" resolve="Dependency" />
                </node>
              </node>
              <node concept="2OqwBi" id="6sC7QXwVa_p" role="33vP2m">
                <node concept="2OqwBi" id="6sC7QXwVa_q" role="2Oq$k0">
                  <node concept="2OqwBi" id="6sC7QXwVa_r" role="2Oq$k0">
                    <node concept="2OqwBi" id="6sC7QXwVa_s" role="2Oq$k0">
                      <node concept="0IXxy" id="6sC7QXwVa_t" role="2Oq$k0" />
                      <node concept="2Xjw5R" id="6sC7QXwVa_u" role="2OqNvi">
                        <node concept="1xMEDy" id="6sC7QXwVa_v" role="1xVPHs">
                          <node concept="chp4Y" id="6sC7QXwVa_w" role="ri$Ld">
                            <ref role="cht4Q" to="ktbj:5pu6noS52gF" resolve="ComponentSet" />
                          </node>
                        </node>
                      </node>
                    </node>
                    <node concept="3Tsc0h" id="6sC7QXwVa_x" role="2OqNvi">
                      <ref role="3TtcxE" to="ktbj:5pu6noS56YC" resolve="component" />
                    </node>
                  </node>
                  <node concept="3goQfb" id="6sC7QXwVa_y" role="2OqNvi">
                    <node concept="1bVj0M" id="6sC7QXwVa_z" role="23t8la">
                      <node concept="3clFbS" id="6sC7QXwVa_$" role="1bW5cS">
                        <node concept="3clFbF" id="6sC7QXwVa__" role="3cqZAp">
                          <node concept="2OqwBi" id="6sC7QXwVa_A" role="3clFbG">
                            <node concept="2OqwBi" id="6sC7QXwVa_B" role="2Oq$k0">
                              <node concept="37vLTw" id="6sC7QXwVa_C" role="2Oq$k0">
                                <ref role="3cqZAo" node="5W7E4fV0WXJ" resolve="it" />
                              </node>
                              <node concept="3Tsc0h" id="6sC7QXwVa_D" role="2OqNvi">
                                <ref role="3TtcxE" to="ktbj:5pu6noS5f57" resolve="dep" />
                              </node>
                            </node>
                            <node concept="3zZkjj" id="6sC7QXwVa_E" role="2OqNvi">
                              <node concept="1bVj0M" id="6sC7QXwVa_F" role="23t8la">
                                <node concept="3clFbS" id="6sC7QXwVa_G" role="1bW5cS">
                                  <node concept="3clFbF" id="6sC7QXwVa_H" role="3cqZAp">
                                    <node concept="3clFbC" id="6sC7QXwVa_I" role="3clFbG">
                                      <node concept="0IXxy" id="6sC7QXwVa_J" role="3uHU7w" />
                                      <node concept="2OqwBi" id="6sC7QXwVa_K" role="3uHU7B">
                                        <node concept="37vLTw" id="6sC7QXwVa_L" role="2Oq$k0">
                                          <ref role="3cqZAo" node="5W7E4fV0WXH" resolve="it" />
                                        </node>
                                        <node concept="3TrEf2" id="6sC7QXwVa_M" role="2OqNvi">
                                          <ref role="3Tt5mk" to="ktbj:5pu6noS6Rpk" resolve="to" />
                                        </node>
                                      </node>
                                    </node>
                                  </node>
                                </node>
                                <node concept="gl6BB" id="5W7E4fV0WXH" role="1bW2Oz">
                                  <property role="TrG5h" value="it" />
                                  <node concept="2jxLKc" id="5W7E4fV0WXI" role="1tU5fm" />
                                </node>
                              </node>
                            </node>
                          </node>
                        </node>
                      </node>
                      <node concept="gl6BB" id="5W7E4fV0WXJ" role="1bW2Oz">
                        <property role="TrG5h" value="it" />
                        <node concept="2jxLKc" id="5W7E4fV0WXK" role="1tU5fm" />
                      </node>
                    </node>
                  </node>
                </node>
                <node concept="ANE8D" id="6sC7QXwVa_R" role="2OqNvi" />
              </node>
            </node>
          </node>
          <node concept="3clFbF" id="6sC7QXwUWi3" role="3cqZAp">
            <node concept="2OqwBi" id="6sC7QXwVbtg" role="3clFbG">
              <node concept="37vLTw" id="6sC7QXwVa_S" role="2Oq$k0">
                <ref role="3cqZAo" node="6sC7QXwVa_o" resolve="list" />
              </node>
              <node concept="2es0OD" id="6sC7QXwVdaX" role="2OqNvi">
                <node concept="1bVj0M" id="6sC7QXwVdaZ" role="23t8la">
                  <node concept="3clFbS" id="6sC7QXwVdb0" role="1bW5cS">
                    <node concept="3clFbF" id="6sC7QXwVdeL" role="3cqZAp">
                      <node concept="2OqwBi" id="6sC7QXwVdi2" role="3clFbG">
                        <node concept="37vLTw" id="6sC7QXwVdeK" role="2Oq$k0">
                          <ref role="3cqZAo" node="5W7E4fV0WXL" resolve="it" />
                        </node>
                        <node concept="3YRAZt" id="6sC7QXwVdy2" role="2OqNvi" />
                      </node>
                    </node>
                  </node>
                  <node concept="gl6BB" id="5W7E4fV0WXL" role="1bW2Oz">
                    <property role="TrG5h" value="it" />
                    <node concept="2jxLKc" id="5W7E4fV0WXM" role="1tU5fm" />
                  </node>
                </node>
              </node>
            </node>
          </node>
          <node concept="3clFbF" id="6sC7QXwVe0N" role="3cqZAp">
            <node concept="2OqwBi" id="6sC7QXwVecW" role="3clFbG">
              <node concept="0IXxy" id="6sC7QXwVe0L" role="2Oq$k0" />
              <node concept="3YRAZt" id="6sC7QXwVezH" role="2OqNvi" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="1h_SRR" id="6sC7QXwVfkA">
    <property role="TrG5h" value="delConnector" />
    <ref role="1h_SK9" to="ktbj:5pu6noS6R6w" resolve="Dependency" />
    <node concept="1hA7zw" id="6sC7QXwVfkB" role="1h_SK8">
      <property role="1hAc7j" value="g_hAxAO/delete_action_id" />
      <node concept="1hAIg9" id="6sC7QXwVfkC" role="1hA7z_">
        <node concept="3clFbS" id="6sC7QXwVfkD" role="2VODD2">
          <node concept="3clFbF" id="6sC7QXwVfkI" role="3cqZAp">
            <node concept="2OqwBi" id="6sC7QXwVflQ" role="3clFbG">
              <node concept="0IXxy" id="6sC7QXwVfkH" role="2Oq$k0" />
              <node concept="3YRAZt" id="6sC7QXwVfuj" role="2OqNvi" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="U5sb5SH2Y3">
    <ref role="1XX52x" to="ktbj:5pu6noS6R6w" resolve="Dependency" />
    <node concept="3F0ifn" id="U5sb5SHy_B" role="2wV5jI">
      <property role="3F0ifm" value="+" />
    </node>
    <node concept="2aJ2om" id="U5sb5SHy$w" role="CpUAK">
      <ref role="2$4xQ3" node="54Q_hb054Do" resolve="table" />
    </node>
  </node>
  <node concept="24kQdi" id="U5sb5SHy_E">
    <ref role="1XX52x" to="ktbj:5pu6noS6Y5A" resolve="InPort" />
    <node concept="XafU7" id="U5sb5SHyRT" role="2wV5jI">
      <node concept="3TQVft" id="U5sb5SHyRV" role="3TRxkO">
        <node concept="3TQlhw" id="U5sb5SHyRX" role="3TQWv3">
          <node concept="3clFbS" id="U5sb5SHyRZ" role="2VODD2">
            <node concept="3clFbF" id="U5sb5SHS_o" role="3cqZAp">
              <node concept="2OqwBi" id="U5sb5SI38D" role="3clFbG">
                <node concept="2OqwBi" id="U5sb5SHSDQ" role="2Oq$k0">
                  <node concept="pncrf" id="U5sb5SHS_n" role="2Oq$k0" />
                  <node concept="2Xjw5R" id="U5sb5SI2Ju" role="2OqNvi">
                    <node concept="1xMEDy" id="U5sb5SI2Jw" role="1xVPHs">
                      <node concept="chp4Y" id="U5sb5SI2UK" role="ri$Ld">
                        <ref role="cht4Q" to="ktbj:5pu6noS5f54" resolve="Component" />
                      </node>
                    </node>
                  </node>
                </node>
                <node concept="3TrcHB" id="U5sb5SI3pn" role="2OqNvi">
                  <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3TQsA7" id="U5sb5SHyS1" role="3TQXYj">
          <node concept="3clFbS" id="U5sb5SHyS3" role="2VODD2" />
        </node>
        <node concept="3TQwEX" id="U5sb5SHyS5" role="3TQZqC">
          <node concept="3clFbS" id="U5sb5SHyS7" role="2VODD2">
            <node concept="3clFbF" id="U5sb5SHSqN" role="3cqZAp">
              <node concept="3clFbT" id="U5sb5SHSqM" role="3clFbG">
                <property role="3clFbU" value="true" />
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
    <node concept="2aJ2om" id="U5sb5SHy_G" role="CpUAK">
      <ref role="2$4xQ3" node="54Q_hb054Do" resolve="table" />
    </node>
  </node>
  <node concept="24kQdi" id="U5sb5SI3JU">
    <ref role="1XX52x" to="ktbj:5pu6noS6Y55" resolve="OutPort" />
    <node concept="XafU7" id="U5sb5SI3JV" role="2wV5jI">
      <node concept="3TQVft" id="U5sb5SI3JW" role="3TRxkO">
        <node concept="3TQlhw" id="U5sb5SI3JX" role="3TQWv3">
          <node concept="3clFbS" id="U5sb5SI3JY" role="2VODD2">
            <node concept="3clFbF" id="U5sb5SI3JZ" role="3cqZAp">
              <node concept="2OqwBi" id="U5sb5SI3K0" role="3clFbG">
                <node concept="2OqwBi" id="U5sb5SI3K1" role="2Oq$k0">
                  <node concept="pncrf" id="U5sb5SI3K2" role="2Oq$k0" />
                  <node concept="2Xjw5R" id="U5sb5SI3K3" role="2OqNvi">
                    <node concept="1xMEDy" id="U5sb5SI3K4" role="1xVPHs">
                      <node concept="chp4Y" id="U5sb5SI3K5" role="ri$Ld">
                        <ref role="cht4Q" to="ktbj:5pu6noS5f54" resolve="Component" />
                      </node>
                    </node>
                  </node>
                </node>
                <node concept="3TrcHB" id="U5sb5SI3K6" role="2OqNvi">
                  <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3TQsA7" id="U5sb5SI3K7" role="3TQXYj">
          <node concept="3clFbS" id="U5sb5SI3K8" role="2VODD2" />
        </node>
        <node concept="3TQwEX" id="U5sb5SI3K9" role="3TQZqC">
          <node concept="3clFbS" id="U5sb5SI3Ka" role="2VODD2">
            <node concept="3clFbF" id="U5sb5SI3Kb" role="3cqZAp">
              <node concept="3clFbT" id="U5sb5SI3Kc" role="3clFbG">
                <property role="3clFbU" value="true" />
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
    <node concept="2aJ2om" id="U5sb5SI3Kd" role="CpUAK">
      <ref role="2$4xQ3" node="54Q_hb054Do" resolve="table" />
    </node>
  </node>
  <node concept="24kQdi" id="74C6il$lkm$">
    <ref role="1XX52x" to="ktbj:5pu6noS6Y5A" resolve="InPort" />
    <node concept="3YTeF2" id="74C6il$lkmC" role="2wV5jI">
      <property role="3YT9PZ" value="true" />
    </node>
    <node concept="2aJ2om" id="74C6il$lkmA" role="CpUAK">
      <ref role="2$4xQ3" node="5pu6noS9YPC" resolve="diagram" />
    </node>
  </node>
  <node concept="24kQdi" id="74C6il$lkF7">
    <ref role="1XX52x" to="ktbj:5pu6noS6Y55" resolve="OutPort" />
    <node concept="3YTeF2" id="74C6il$lkPt" role="2wV5jI" />
    <node concept="2aJ2om" id="74C6il$lkPr" role="CpUAK">
      <ref role="2$4xQ3" node="5pu6noS9YPC" resolve="diagram" />
    </node>
  </node>
  <node concept="312cEu" id="HEilRNynZA">
    <property role="TrG5h" value="CustomNamedBoxFigure" />
    <node concept="2tJIrI" id="1ZQTqiPodNM" role="jymVt" />
    <node concept="312cEg" id="4UC9Eb7y_Ae" role="jymVt">
      <property role="TrG5h" value="myCell" />
      <property role="eg7rD" value="false" />
      <property role="34CwA1" value="false" />
      <property role="3TUv4t" value="false" />
      <node concept="3uibUv" id="4UC9Eb7y_Ag" role="1tU5fm">
        <ref role="3uigEE" to="d7dq:~TextCell" resolve="TextCell" />
      </node>
      <node concept="2ShNRf" id="4UC9Eb7y_G4" role="33vP2m">
        <node concept="1pGfFk" id="4UC9Eb7y_G5" role="2ShVmc">
          <ref role="37wK5l" to="d7dq:~TextCell.&lt;init&gt;()" resolve="TextCell" />
        </node>
      </node>
      <node concept="3Tm6S6" id="4UC9Eb7y_Ai" role="1B3o_S" />
    </node>
    <node concept="2tJIrI" id="1ZQTqiPmqcE" role="jymVt" />
    <node concept="3clFbW" id="74C6il$q$qA" role="jymVt">
      <node concept="3cqZAl" id="74C6il$q$qB" role="3clF45" />
      <node concept="3Tm1VV" id="74C6il$q$qC" role="1B3o_S" />
      <node concept="3clFbS" id="74C6il$q$qD" role="3clF47">
        <node concept="1VxSAg" id="1ZQTqiPn1Pp" role="3cqZAp">
          <ref role="37wK5l" node="HEilRNz$Gf" resolve="CustomNamedBoxFigure" />
          <node concept="2ShNRf" id="1ZQTqiPn76h" role="37wK5m">
            <node concept="HV5vD" id="1ZQTqiPn9Uq" role="2ShVmc">
              <ref role="HV5vE" node="1ZQTqiPlP6Z" resolve="CustomNamedBoxFigure.CustomNamedBoxFigureMapperFactory" />
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="74C6il$pA82" role="3cqZAp">
          <node concept="2OqwBi" id="74C6il$pAkX" role="3clFbG">
            <node concept="1rXfSq" id="74C6il$pA81" role="2Oq$k0">
              <ref role="37wK5l" to="jqfx:~View.background()" resolve="background" />
            </node>
            <node concept="liA8E" id="74C6il$pBqS" role="2OqNvi">
              <ref role="37wK5l" to="lgza:~WritableProperty.set(java.lang.Object)" resolve="set" />
              <node concept="10M0yZ" id="74C6il$pBwb" role="37wK5m">
                <ref role="3cqZAo" to="4rj2:~Color.LIGHT_YELLOW" resolve="LIGHT_YELLOW" />
                <ref role="1PxDUh" to="4rj2:~Color" resolve="Color" />
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
    <node concept="3clFbW" id="HEilRNz$Gf" role="jymVt">
      <node concept="3cqZAl" id="HEilRNz$Gh" role="3clF45" />
      <node concept="3Tm1VV" id="HEilRNz$Gi" role="1B3o_S" />
      <node concept="3clFbS" id="1ZQTqiPlN1y" role="3clF47">
        <node concept="3cpWs8" id="4UC9Eb7y_AA" role="3cqZAp">
          <node concept="3cpWsn" id="4UC9Eb7y_A_" role="3cpWs9">
            <property role="TrG5h" value="cellView" />
            <property role="3TUv4t" value="false" />
            <node concept="3uibUv" id="2kp0uDALmxb" role="1tU5fm">
              <ref role="3uigEE" to="d0r4:~CellView" resolve="CellView" />
            </node>
            <node concept="2ShNRf" id="4UC9Eb7y_Ga" role="33vP2m">
              <node concept="1pGfFk" id="4UC9Eb7y_Gb" role="2ShVmc">
                <ref role="37wK5l" to="d0r4:~CellView.&lt;init&gt;()" resolve="CellView" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="4UC9Eb7y_AG" role="3cqZAp">
          <node concept="2OqwBi" id="4UC9Eb7y_AH" role="3clFbG">
            <node concept="2OqwBi" id="4UC9Eb7y_Gk" role="2Oq$k0">
              <node concept="37vLTw" id="4UC9Eb7y_Gj" role="2Oq$k0">
                <ref role="3cqZAo" node="4UC9Eb7y_Ae" resolve="myCell" />
              </node>
              <node concept="liA8E" id="4UC9Eb7y_Gl" role="2OqNvi">
                <ref role="37wK5l" to="d7dq:~TextCell.textColor()" resolve="textColor" />
              </node>
            </node>
            <node concept="liA8E" id="4UC9Eb7y_AJ" role="2OqNvi">
              <ref role="37wK5l" to="lgza:~WritableProperty.set(java.lang.Object)" resolve="set" />
              <node concept="10M0yZ" id="4UC9Eb7$fB1" role="37wK5m">
                <ref role="1PxDUh" to="4rj2:~Color" resolve="Color" />
                <ref role="3cqZAo" to="4rj2:~Color.BLACK" resolve="BLACK" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="1ZQTqiPnu3E" role="3cqZAp">
          <node concept="2OqwBi" id="1ZQTqiPnvCL" role="3clFbG">
            <node concept="2OqwBi" id="1ZQTqiPnuEf" role="2Oq$k0">
              <node concept="37vLTw" id="1ZQTqiPnu3D" role="2Oq$k0">
                <ref role="3cqZAo" node="4UC9Eb7y_Ae" resolve="myCell" />
              </node>
              <node concept="liA8E" id="1ZQTqiPnvvj" role="2OqNvi">
                <ref role="37wK5l" to="d7dq:~TextCell.text()" resolve="text" />
              </node>
            </node>
            <node concept="liA8E" id="1ZQTqiPnwwl" role="2OqNvi">
              <ref role="37wK5l" to="lgza:~WritableProperty.set(java.lang.Object)" resolve="set" />
              <node concept="Xl_RD" id="1ZQTqiPnwBB" role="37wK5m">
                <property role="Xl_RC" value="&lt;&lt;No text&gt;&gt;" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="4UC9Eb7y_AL" role="3cqZAp">
          <node concept="2OqwBi" id="4UC9Eb7y_Gr" role="3clFbG">
            <node concept="2OqwBi" id="4UC9Eb7y_Gp" role="2Oq$k0">
              <node concept="37vLTw" id="1ZQTqiPmIwm" role="2Oq$k0">
                <ref role="3cqZAo" node="4UC9Eb7y_A_" resolve="cellView" />
              </node>
              <node concept="2OwXpG" id="4UC9Eb7y_Gq" role="2OqNvi">
                <ref role="2Oxat5" to="d0r4:~CellView.cell" resolve="cell" />
              </node>
            </node>
            <node concept="liA8E" id="4UC9Eb7y_Gs" role="2OqNvi">
              <ref role="37wK5l" to="lgza:~WritableProperty.set(java.lang.Object)" resolve="set" />
              <node concept="37vLTw" id="4UC9Eb7y_AN" role="37wK5m">
                <ref role="3cqZAo" node="4UC9Eb7y_Ae" resolve="myCell" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbF" id="1ZQTqiPmLlJ" role="3cqZAp">
          <node concept="2OqwBi" id="1ZQTqiPmLT4" role="3clFbG">
            <node concept="1rXfSq" id="1ZQTqiPmLlI" role="2Oq$k0">
              <ref role="37wK5l" to="jqfx:~View.children()" resolve="children" />
            </node>
            <node concept="liA8E" id="1ZQTqiPmNr3" role="2OqNvi">
              <ref role="37wK5l" to="33ny:~List.add(java.lang.Object)" resolve="add" />
              <node concept="37vLTw" id="1ZQTqiPmO22" role="37wK5m">
                <ref role="3cqZAo" node="4UC9Eb7y_A_" resolve="cellView" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbJ" id="1ZQTqiPn31u" role="3cqZAp">
          <node concept="3clFbS" id="1ZQTqiPn31x" role="3clFbx">
            <node concept="3clFbF" id="1ZQTqiPn4xV" role="3cqZAp">
              <node concept="2OqwBi" id="1ZQTqiPn57c" role="3clFbG">
                <node concept="2OqwBi" id="1ZQTqiPn4AR" role="2Oq$k0">
                  <node concept="37vLTw" id="1ZQTqiPn4xU" role="2Oq$k0">
                    <ref role="3cqZAo" node="1ZQTqiPn1PF" resolve="factory" />
                  </node>
                  <node concept="liA8E" id="1ZQTqiPn4Wa" role="2OqNvi">
                    <ref role="37wK5l" node="1ZQTqiPlP70" resolve="createMapper" />
                    <node concept="Xjq3P" id="1ZQTqiPn4ZI" role="37wK5m" />
                  </node>
                </node>
                <node concept="liA8E" id="1ZQTqiPn5vp" role="2OqNvi">
                  <ref role="37wK5l" to="sm7x:~Mapper.attachRoot()" resolve="attachRoot" />
                </node>
              </node>
            </node>
          </node>
          <node concept="3y3z36" id="1ZQTqiPn488" role="3clFbw">
            <node concept="10Nm6u" id="1ZQTqiPn4x9" role="3uHU7w" />
            <node concept="37vLTw" id="1ZQTqiPn3uw" role="3uHU7B">
              <ref role="3cqZAo" node="1ZQTqiPn1PF" resolve="factory" />
            </node>
          </node>
        </node>
      </node>
      <node concept="37vLTG" id="1ZQTqiPn1PF" role="3clF46">
        <property role="TrG5h" value="factory" />
        <node concept="3uibUv" id="1ZQTqiPn1PE" role="1tU5fm">
          <ref role="3uigEE" node="1ZQTqiPlP6Z" resolve="CustomNamedBoxFigure.CustomNamedBoxFigureMapperFactory" />
        </node>
      </node>
    </node>
    <node concept="3clFb_" id="4UC9Eb7KHBQ" role="jymVt">
      <property role="od$2w" value="false" />
      <property role="TrG5h" value="idText" />
      <property role="DiZV1" value="false" />
      <node concept="3clFbS" id="4UC9Eb7KHBR" role="3clF47">
        <node concept="3clFbF" id="4UC9Eb7KHBS" role="3cqZAp">
          <node concept="2OqwBi" id="4UC9Eb7KHC0" role="3clFbG">
            <node concept="37vLTw" id="4UC9Eb7KHBZ" role="2Oq$k0">
              <ref role="3cqZAo" node="4UC9Eb7y_Ae" resolve="myCell" />
            </node>
            <node concept="liA8E" id="4UC9Eb7KHC1" role="2OqNvi">
              <ref role="37wK5l" to="d7dq:~TextCell.text()" resolve="text" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3Tm1VV" id="4UC9Eb7KHBU" role="1B3o_S" />
      <node concept="3uibUv" id="4UC9Eb7KHBV" role="3clF45">
        <ref role="3uigEE" to="lgza:~Property" resolve="Property" />
        <node concept="17QB3L" id="4UC9Eb7KSTk" role="11_B2D" />
      </node>
      <node concept="zeN4a" id="4UC9Eb7LTfO" role="lGtFl" />
    </node>
    <node concept="2tJIrI" id="1ZQTqiPmZro" role="jymVt" />
    <node concept="312cEu" id="1ZQTqiPlP6Z" role="jymVt">
      <property role="TrG5h" value="CustomNamedBoxFigureMapperFactory" />
      <property role="2bfB8j" value="false" />
      <node concept="3clFb_" id="1ZQTqiPlP70" role="jymVt">
        <property role="1EzhhJ" value="false" />
        <property role="TrG5h" value="createMapper" />
        <property role="DiZV1" value="false" />
        <node concept="3Tm1VV" id="1ZQTqiPlP71" role="1B3o_S" />
        <node concept="3uibUv" id="1ZQTqiPlP72" role="3clF45">
          <ref role="3uigEE" to="sm7x:~Mapper" resolve="Mapper" />
          <node concept="3qUE_q" id="1ZQTqiPlP73" role="11_B2D">
            <node concept="3uibUv" id="74C6il$qL2X" role="3qUE_r">
              <ref role="3uigEE" node="HEilRNynZA" resolve="CustomNamedBoxFigure" />
            </node>
          </node>
          <node concept="3qUE_q" id="1ZQTqiPlP75" role="11_B2D">
            <node concept="3uibUv" id="74C6il$qMAe" role="3qUE_r">
              <ref role="3uigEE" node="HEilRNynZA" resolve="CustomNamedBoxFigure" />
            </node>
          </node>
        </node>
        <node concept="37vLTG" id="1ZQTqiPlP77" role="3clF46">
          <property role="TrG5h" value="figure" />
          <property role="3TUv4t" value="true" />
          <node concept="3uibUv" id="74C6il$qOeR" role="1tU5fm">
            <ref role="3uigEE" node="HEilRNynZA" resolve="CustomNamedBoxFigure" />
          </node>
        </node>
        <node concept="3clFbS" id="1ZQTqiPlP79" role="3clF47">
          <node concept="3cpWs6" id="1ZQTqiPlP7a" role="3cqZAp">
            <node concept="2ShNRf" id="1ZQTqiPlP7b" role="3cqZAk">
              <node concept="YeOm9" id="74C6il$tb_S" role="2ShVmc">
                <node concept="1Y3b0j" id="74C6il$tb_V" role="YeSDq">
                  <property role="2bfB8j" value="true" />
                  <ref role="1Y3XeK" to="8tro:1ZQTqiPlQJx" resolve="NamedBoxFigure.NamedBoxFigureMapper" />
                  <ref role="37wK5l" to="8tro:1ZQTqiPlYad" resolve="NamedBoxFigure.NamedBoxFigureMapper" />
                  <node concept="3Tm1VV" id="74C6il$tb_W" role="1B3o_S" />
                  <node concept="37vLTw" id="1ZQTqiPm1UL" role="37wK5m">
                    <ref role="3cqZAo" node="1ZQTqiPlP77" resolve="figure" />
                  </node>
                  <node concept="3uibUv" id="74C6il$tcuk" role="2Ghqu4">
                    <ref role="3uigEE" node="HEilRNynZA" resolve="CustomNamedBoxFigure" />
                  </node>
                  <node concept="3clFb_" id="74C6il$y4Nc" role="jymVt">
                    <property role="1EzhhJ" value="false" />
                    <property role="TrG5h" value="registerSynchronizers" />
                    <property role="DiZV1" value="false" />
                    <node concept="3Tmbuc" id="74C6il$y4Nd" role="1B3o_S" />
                    <node concept="3cqZAl" id="74C6il$y4Ne" role="3clF45" />
                    <node concept="37vLTG" id="74C6il$y4Nf" role="3clF46">
                      <property role="TrG5h" value="configuration" />
                      <node concept="3uibUv" id="74C6il$y4Ng" role="1tU5fm">
                        <ref role="3uigEE" to="sm7x:~Mapper$SynchronizersConfiguration" resolve="Mapper.SynchronizersConfiguration" />
                      </node>
                    </node>
                    <node concept="2AHcQZ" id="74C6il$y4Nh" role="2AJF6D">
                      <ref role="2AI5Lk" to="wyt6:~Override" resolve="Override" />
                    </node>
                    <node concept="3clFbS" id="74C6il$y4O7" role="3clF47">
                      <node concept="3clFbF" id="74C6il$y4Oa" role="3cqZAp">
                        <node concept="3nyPlj" id="74C6il$y4O9" role="3clFbG">
                          <ref role="37wK5l" to="8tro:1ZQTqiPlYst" resolve="registerSynchronizers" />
                          <node concept="37vLTw" id="74C6il$y4O8" role="37wK5m">
                            <ref role="3cqZAo" node="74C6il$y4Nf" resolve="configuration" />
                          </node>
                        </node>
                      </node>
                      <node concept="3clFbF" id="74C6il$y5p4" role="3cqZAp">
                        <node concept="2OqwBi" id="74C6il$y5tl" role="3clFbG">
                          <node concept="37vLTw" id="74C6il$y5p3" role="2Oq$k0">
                            <ref role="3cqZAo" node="74C6il$y4Nf" resolve="configuration" />
                          </node>
                          <node concept="liA8E" id="74C6il$y63Z" role="2OqNvi">
                            <ref role="37wK5l" to="sm7x:~Mapper$SynchronizersConfiguration.add(jetbrains.jetpad.mapper.Synchronizer)" resolve="add" />
                            <node concept="2YIFZM" id="74C6il$y6tA" role="37wK5m">
                              <ref role="1Pybhc" to="sm7x:~Synchronizers" resolve="Synchronizers" />
                              <ref role="37wK5l" to="sm7x:~Synchronizers.forProperty(jetbrains.jetpad.model.property.ReadableProperty,jetbrains.jetpad.model.property.WritableProperty)" resolve="forProperty" />
                              <node concept="2OqwBi" id="74C6il$yitJ" role="37wK5m">
                                <node concept="37vLTw" id="74C6il$y6Hd" role="2Oq$k0">
                                  <ref role="3cqZAo" node="1ZQTqiPlP77" resolve="figure" />
                                </node>
                                <node concept="liA8E" id="74C6il$yjPX" role="2OqNvi">
                                  <ref role="37wK5l" to="jqfx:~View.parent()" resolve="parent" />
                                </node>
                              </node>
                              <node concept="1bVj0M" id="74C6il$yhyB" role="37wK5m">
                                <node concept="37vLTG" id="74C6il$yhZU" role="1bW2Oz">
                                  <property role="TrG5h" value="parentView" />
                                  <node concept="3uibUv" id="74C6il$ylvq" role="1tU5fm">
                                    <ref role="3uigEE" to="jqfx:~View" resolve="View" />
                                  </node>
                                </node>
                                <node concept="3clFbS" id="74C6il$yhyD" role="1bW5cS">
                                  <node concept="2$JKZl" id="74C6il$ynZI" role="3cqZAp">
                                    <node concept="3clFbS" id="74C6il$ynZJ" role="2LFqv$">
                                      <node concept="3clFbJ" id="74C6il$yoU2" role="3cqZAp">
                                        <node concept="3clFbS" id="74C6il$yoU3" role="3clFbx">
                                          <node concept="3clFbF" id="74C6il$yqzd" role="3cqZAp">
                                            <node concept="2OqwBi" id="74C6il$yqYy" role="3clFbG">
                                              <node concept="1eOMI4" id="74C6il$yqz9" role="2Oq$k0">
                                                <node concept="10QFUN" id="74C6il$yqz6" role="1eOMHV">
                                                  <node concept="3uibUv" id="74C6il$yqzb" role="10QFUM">
                                                    <ref role="3uigEE" to="zdnc:~DiagramNodeView" resolve="DiagramNodeView" />
                                                  </node>
                                                  <node concept="37vLTw" id="74C6il$yqzc" role="10QFUP">
                                                    <ref role="3cqZAo" node="74C6il$yhZU" resolve="parentView" />
                                                  </node>
                                                </node>
                                              </node>
                                              <node concept="liA8E" id="74C6il$ys0c" role="2OqNvi">
                                                <ref role="37wK5l" to="zdnc:~DiagramNodeView.setPortsDirection(jetbrains.jetpad.projectional.diagram.base.GridDirection)" resolve="setPortsDirection" />
                                                <node concept="Rm8GO" id="6mo44cyslsg" role="37wK5m">
                                                  <ref role="Rm8GQ" to="mgas:~GridDirection.DOWN" resolve="DOWN" />
                                                  <ref role="1Px2BO" to="mgas:~GridDirection" resolve="GridDirection" />
                                                </node>
                                              </node>
                                            </node>
                                          </node>
                                        </node>
                                        <node concept="2ZW3vV" id="74C6il$ypLf" role="3clFbw">
                                          <node concept="3uibUv" id="74C6il$yqg7" role="2ZW6by">
                                            <ref role="3uigEE" to="zdnc:~DiagramNodeView" resolve="DiagramNodeView" />
                                          </node>
                                          <node concept="37vLTw" id="74C6il$ypuq" role="2ZW6bz">
                                            <ref role="3cqZAo" node="74C6il$yhZU" resolve="parentView" />
                                          </node>
                                        </node>
                                      </node>
                                      <node concept="3clFbF" id="6mo44cypLy9" role="3cqZAp">
                                        <node concept="37vLTI" id="6mo44cypMkU" role="3clFbG">
                                          <node concept="2OqwBi" id="6mo44cypOK0" role="37vLTx">
                                            <node concept="2OqwBi" id="6mo44cypMUd" role="2Oq$k0">
                                              <node concept="37vLTw" id="6mo44cypMur" role="2Oq$k0">
                                                <ref role="3cqZAo" node="74C6il$yhZU" resolve="parentView" />
                                              </node>
                                              <node concept="liA8E" id="6mo44cypOaN" role="2OqNvi">
                                                <ref role="37wK5l" to="jqfx:~View.parent()" resolve="parent" />
                                              </node>
                                            </node>
                                            <node concept="liA8E" id="6mo44cypQAM" role="2OqNvi">
                                              <ref role="37wK5l" to="lgza:~ReadableProperty.get()" resolve="get" />
                                            </node>
                                          </node>
                                          <node concept="37vLTw" id="6mo44cypLy8" role="37vLTJ">
                                            <ref role="3cqZAo" node="74C6il$yhZU" resolve="parentView" />
                                          </node>
                                        </node>
                                      </node>
                                    </node>
                                    <node concept="3y3z36" id="74C6il$yors" role="2$JKZa">
                                      <node concept="10Nm6u" id="74C6il$yo$j" role="3uHU7w" />
                                      <node concept="37vLTw" id="74C6il$yo8r" role="3uHU7B">
                                        <ref role="3cqZAo" node="74C6il$yhZU" resolve="parentView" />
                                      </node>
                                    </node>
                                  </node>
                                </node>
                              </node>
                            </node>
                          </node>
                        </node>
                      </node>
                    </node>
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
      <node concept="3Tm6S6" id="1ZQTqiPlP7e" role="1B3o_S" />
      <node concept="3uibUv" id="1ZQTqiPlP7f" role="EKbjA">
        <ref role="3uigEE" to="sm7x:~MapperFactory" resolve="MapperFactory" />
        <node concept="3uibUv" id="74C6il$qICc" role="11_B2D">
          <ref role="3uigEE" node="HEilRNynZA" resolve="CustomNamedBoxFigure" />
        </node>
        <node concept="3uibUv" id="74C6il$qJQG" role="11_B2D">
          <ref role="3uigEE" node="HEilRNynZA" resolve="CustomNamedBoxFigure" />
        </node>
      </node>
    </node>
    <node concept="2tJIrI" id="74C6il$q$cC" role="jymVt" />
    <node concept="3Tm1VV" id="HEilRNynZB" role="1B3o_S" />
    <node concept="3uibUv" id="74C6il$rHXZ" role="1zkMxy">
      <ref role="3uigEE" to="8tro:HEilRNynZA" resolve="NamedBoxFigure" />
    </node>
    <node concept="3FP93d" id="HEilRNywb_" role="lGtFl" />
  </node>
</model>

