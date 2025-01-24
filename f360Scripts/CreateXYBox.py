import adsk.core, adsk.fusion, adsk.cam, traceback

def create_rectangle():
    app = adsk.core.Application.get()
    ui = app.userInterface

    class RectangleCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
        def __init__(self):
            super().__init__()

        def notify(self, args):
            try:
                command = args.command
                inputs = command.commandInputs

                # Add inputs for rectangle dimensions
                inputs.addValueInput('xWidth', 'Width (X)', 'cm', adsk.core.ValueInput.createByString('10'))
                inputs.addValueInput('yWidth', 'Height (Y)', 'cm', adsk.core.ValueInput.createByString('20'))

                on_execute = RectangleCommandExecuteHandler()
                command.execute.add(on_execute)
                handlers.append(on_execute)
            except Exception as e:
                if ui:
                    ui.messageBox(f'Failed in commandCreated: {traceback.format_exc()}')

    class RectangleCommandExecuteHandler(adsk.core.CommandEventHandler):
        def __init__(self):
            super().__init__()

        def notify(self, args):
            try:
                unitsMgr = app.activeProduct.unitsManager
                command = args.firingEvent.sender
                inputs = command.commandInputs

                x_width = 0
                y_width = 0

                for input in inputs:
                    if input.id == 'xWidth':
                        x_width = unitsMgr.evaluateExpression(input.expression, "cm")
                    elif input.id == 'yWidth':
                        y_width = unitsMgr.evaluateExpression(input.expression, "cm")

                design = app.activeProduct
                if not design or not isinstance(design, adsk.fusion.Design):
                    ui.messageBox('Please switch to a Fusion Design workspace to run this command.')
                    return

                root_comp = design.rootComponent
                sketches = root_comp.sketches
                xy_plane = root_comp.xYConstructionPlane
                sketch = sketches.add(xy_plane)

                point1 = adsk.core.Point3D.create(0, 0, 0)
                point2 = adsk.core.Point3D.create(x_width, 0, 0)
                point3 = adsk.core.Point3D.create(x_width, y_width, 0)
                point4 = adsk.core.Point3D.create(0, y_width, 0)

                sketch.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
                sketch.sketchCurves.sketchLines.addByTwoPoints(point2, point3)
                sketch.sketchCurves.sketchLines.addByTwoPoints(point3, point4)
                sketch.sketchCurves.sketchLines.addByTwoPoints(point4, point1)

                ui.messageBox(f'Rectangle created with dimensions: {x_width} cm x {y_width} cm')

            except Exception as e:
                if ui:
                    ui.messageBox(f'Failed in execute: {traceback.format_exc()}')

    def create_rectangle_command():
        cmd_def = ui.commandDefinitions.itemById('createRectangle')
        if not cmd_def:
            cmd_def = ui.commandDefinitions.addButtonDefinition('createRectangle', 'Create Rectangle', 'Creates a rectangle based on user-defined dimensions.', '')

        on_command_created = RectangleCommandCreatedHandler()
        cmd_def.commandCreated.add(on_command_created)
        handlers.append(on_command_created)

        # Execute the command
        inputs = adsk.core.NamedValues.create()
        ui.commandDefinitions.itemById('createRectangle').execute(inputs)

    try:
        handlers = []
        create_rectangle_command()
        adsk.autoTerminate(False)
    except Exception as e:
        if ui:
            ui.messageBox(f'Failed: {traceback.format_exc()}')

create_rectangle()
