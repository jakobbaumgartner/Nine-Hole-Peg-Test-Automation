def redPoints(center, height, width,s, sin_fi_de, cos_fi_de, sin_fi_mde, cos_fi_mde, delta):
    """calculates and returns a list of points used for detection"""

        # top left

    X_TL = center[0] + s * sin_fi_mde
    Y_TL = center[1] + s * cos_fi_mde

    X_TR = center[0] + s * sin_fi_de
    Y_TR = center[1] + s * cos_fi_de

    X_BL = center[0] - s * sin_fi_de
    Y_BL = center[1] - s * cos_fi_de

    X_BR = center[0] - s * sin_fi_mde
    Y_BR = center[1] - s * cos_fi_mde

    return [ [center[0], center[1]], [X_TL, Y_TL], [X_TR, Y_TR], [X_BL, Y_BL], [X_BR, Y_BR]]