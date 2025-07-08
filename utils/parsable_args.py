import argparse


def check_for_missing_args(**kwargs):
    missing_args = []
    for arg, value in kwargs.items():
        if value is None:
            missing_args.append(arg)
    if missing_args:
        raise ValueError(
            f"Missing required arguments: {', '.join(missing_args)}. "
            "Please provide all required arguments."
        )


def parse_segmentation_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--patient",
        type=str,
        default=None,
        help="Patient ID, e.g. 'NF0014'",
    )
    argparser.add_argument(
        "--well_fov",
        type=str,
        default=None,
        help="Well and field of view to process, e.g. 'A01-1'",
    )
    argparser.add_argument(
        "--clip_limit",
        type=float,
        default=0.03,
        help="Clip limit for contrast enhancement, default is 0.03",
    )
    argparser.add_argument(
        "--twoD_method",
        type=str,
        default="zmax",
        choices=["zmax", "middle"],
        help="Method for 2D projection, either 'zmax' or 'middle'. Default is 'zmax'.",
    )
    args = argparser.parse_args()
    patient = args.patient
    well_fov = args.well_fov
    clip_limit = args.clip_limit
    twoD_method = args.twoD_method

    check_for_missing_args(
        patient=patient,
        well_fov=well_fov,
        clip_limit=clip_limit,
        twoD_method=twoD_method,
    )

    return {
        "patient": patient,
        "well_fov": well_fov,
        "clip_limit": clip_limit,
        "twoD_method": twoD_method,
    }


def parse_featurization_args_patient_and_well_fov():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--well_fov",
        type=str,
        default=None,
        help="Well and field of view to process, e.g. 'A01-1'",
    )
    argparser.add_argument(
        "--patient",
        type=str,
        default=None,
        help="Patient ID, e.g. 'NF0014'",
    )

    args = argparser.parse_args()
    well_fov = args.well_fov
    patient = args.patient

    check_for_missing_args(
        well_fov=well_fov,
        patient=patient,
    )
    return {
        "well_fov": well_fov,
        "patient": patient,
    }


def parse_featurization_args_patient():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--patient",
        type=str,
        default=None,
        help="Patient ID, e.g. 'NF0014'",
    )

    args = argparser.parse_args()
    patient = args.patient

    check_for_missing_args(
        patient=patient,
    )
    return {
        "patient": patient,
    }
