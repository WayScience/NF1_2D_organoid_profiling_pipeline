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


def parse_featurization_args_pateint_and_well_fov():
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
