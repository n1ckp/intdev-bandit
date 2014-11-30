# In Maya, via Python:
import maya.cmds as mc
import maya.mel as mm
import ast

# Our mel global proc.
melproc = """
global proc portData(string $arg){
    python(("portData(\\"" + $arg + "\\")"));
}
"""
mm.eval(melproc)

# Our Python function that can be changed to do whatever we want:
def portData(arg):

    #import the dictionary
    dictIn = ast.literal_eval(arg)

    # move the feet using the recived data
    if mc.objExists('CTRL_FOOT_L'):
        mc.setAttr('CTRL_FOOT_L.translate', float(dictIn['ANKLE_L']['tx']), float(dictIn['ANKLE_L']['ty']), float(dictIn['ANKLE_L']['tz']))
        mc.setAttr('CTRL_FOOT_L.rotate', float(dictIn['ANKLE_L']['rx']), float(dictIn['ANKLE_L']['ry']), float(dictIn['ANKLE_L']['rz']))

    if mc.objExists('CTRL_FOOT_R'):    
        mc.setAttr('CTRL_FOOT_R.translate', float(dictIn['ANKLE_R']['tx']), float(dictIn['ANKLE_R']['ty']), float(dictIn['ANKLE_R']['tz']))
        mc.setAttr('CTRL_FOOT_R.rotate', float(dictIn['ANKLE_R']['rx']), float(dictIn['ANKLE_R']['ry']), float(dictIn['ANKLE_R']['rz']))

# Open the commandPort.  The 'prefix' argument string is calling to the defined
# mel script above (which then calls to our Python function of the same name):
mc.commandPort(name="127.0.0.1:7777", echoOutput=False, noreturn=False,
               prefix="portData", returnNumCommands=True)
