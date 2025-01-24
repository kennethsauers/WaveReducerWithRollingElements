## Credit to Sergei Mishin for the code to generate the cycloid geometry
## His code to visualize the geometry using matplotlib
## https://gist.github.com/mshndev

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

def create_wave_gear():
    app = adsk.core.Application.get()
    ui = app.userInterface

    class WaveGearCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
        def __init__(self):
            super().__init__()

        def notify(self, args):
            try:
                command = args.command
                inputs = command.commandInputs

                # Add inputs for wave gear parameters
                inputs.addValueInput('rollerDiameter', 'Roller Diameter (mm)', 'mm', adsk.core.ValueInput.createByString('5'))
                inputs.addValueInput('rollersNum', 'Number of Rollers', '', adsk.core.ValueInput.createByString('12'))
                inputs.addValueInput('cycloidOuterDiameter', 'Cycloid Outer Diameter (mm)', 'mm', adsk.core.ValueInput.createByString('60'))
                inputs.addValueInput('inputShaftDiameter', 'Input Shaft Diameter (mm)', 'mm', adsk.core.ValueInput.createByString('5'))

                on_execute = WaveGearCommandExecuteHandler()
                command.execute.add(on_execute)
                handlers.append(on_execute)
            except Exception as e:
                if ui:
                    ui.messageBox(f'Failed in commandCreated: {traceback.format_exc()}')

    class WaveGearCommandExecuteHandler(adsk.core.CommandEventHandler):
        def __init__(self):
            super().__init__()

        def notify(self, args):
            try:
                unitsMgr = app.activeProduct.unitsManager
                command = args.firingEvent.sender
                inputs = command.commandInputs

                roller_diameter = 0
                rollers_num = 0
                cycloid_outer_diameter = 0
                input_shaft_diameter = 0

                for input in inputs:
                    if input.id == 'rollerDiameter':
                        roller_diameter = unitsMgr.evaluateExpression(input.expression, "mm")
                    elif input.id == 'rollersNum':
                        rollers_num = int(input.expression)
                    elif input.id == 'cycloidOuterDiameter':
                        cycloid_outer_diameter = unitsMgr.evaluateExpression(input.expression, "mm")
                    elif input.id == 'inputShaftDiameter':
                        input_shaft_diameter = unitsMgr.evaluateExpression(input.expression, "mm")

                ecc = 0.2 * roller_diameter
                cav_num = rollers_num + 1
                cy_r_min = (1.1 * roller_diameter) / math.sin(math.pi / cav_num) + 2 * ecc
                cy_r = max(cycloid_outer_diameter / 2, cy_r_min)
                wave_gen_r = (cy_r - 2 * ecc) - roller_diameter
                roll_r = roller_diameter / 2
                sep_width = 2.2 * ecc
                sep_middle_radius = wave_gen_r + roll_r
                sep_outer_radius = sep_middle_radius + sep_width / 2
                sep_inner_radius = sep_middle_radius - sep_width / 2

                design = app.activeProduct
                if not design or not isinstance(design, adsk.fusion.Design):
                    ui.messageBox('Please switch to a Fusion Design workspace to run this command.')
                    return

                root_comp = design.rootComponent
                sketches = root_comp.sketches
                xy_plane = root_comp.xYConstructionPlane
                sketch = sketches.add(xy_plane)

                # Create cycloidal ring gear points
                points = []
                res = 500
                for i in range(res):
                    theta = (i / res) * 2 * math.pi
                    s_rol = math.sqrt((roll_r + wave_gen_r) ** 2 - (ecc * math.sin(cav_num * theta)) ** 2)
                    l_rol = ecc * math.cos(cav_num * theta) + s_rol
                    xi = math.atan2(ecc * cav_num * math.sin(cav_num * theta), s_rol)
                    x = l_rol * math.sin(theta) + roll_r * math.sin(theta + xi)
                    y = l_rol * math.cos(theta) + roll_r * math.cos(theta + xi)
                    points.append(adsk.core.Point3D.create(x, y, 0))

                # Close the loop
                points.append(points[0])

                # Draw cycloidal ring gear
                for i in range(len(points) - 1):
                    sketch.sketchCurves.sketchLines.addByTwoPoints(points[i], points[i + 1])

                # Draw separator (inner and outer circles)
                sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), sep_outer_radius)
                sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), sep_inner_radius)

                # Draw rollers
                for i in range(rollers_num):
                    theta = i * 2 * math.pi / rollers_num
                    s_rol = math.sqrt((roll_r + wave_gen_r) ** 2 - (ecc * math.sin(cav_num * theta)) ** 2)
                    l_rol = ecc * math.cos(cav_num * theta) + s_rol
                    x = l_rol * math.sin(theta)
                    y = l_rol * math.cos(theta)
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(x, y, 0), roll_r)

                # Draw wave generator
                sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, ecc, 0), wave_gen_r)

                # Draw input shaft hole
                sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), input_shaft_diameter / 2)

                ui.messageBox('Wave gear sketch created successfully.')

            except Exception as e:
                if ui:
                    ui.messageBox(f'Failed in execute: {traceback.format_exc()}')

    def create_wave_gear_command():
        cmd_def = ui.commandDefinitions.itemById('createWaveGear')
        if not cmd_def:
            cmd_def = ui.commandDefinitions.addButtonDefinition('createWaveGear', 'Create Wave Gear', 'Creates a wave gear sketch based on user-defined parameters.', '')

        on_command_created = WaveGearCommandCreatedHandler()
        cmd_def.commandCreated.add(on_command_created)
        handlers.append(on_command_created)

        # Execute the command
        inputs = adsk.core.NamedValues.create()
        ui.commandDefinitions.itemById('createWaveGear').execute(inputs)

    try:
        handlers = []
        create_wave_gear_command()
        adsk.autoTerminate(False)
    except Exception as e:
        if ui:
            ui.messageBox(f'Failed: {traceback.format_exc()}')

create_wave_gear()
