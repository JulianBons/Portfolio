import tensorflow_cloud as tfc

GCP_BUCKET = 'modeldogbreeds'

job_labels = {'job': 'dog_breeds'}

tfc.run(
    entry_point='TrainDogs.py',
    requirements_txt='requirements.txt',
    distribution_strategy='auto',
    chief_config=tfc.MachineConfig(
        cpu_cores=4,
        memory=15,
        accelerator_type=tfc.AcceleratorType.NVIDIA_TESLA_T4,
        accelerator_count=1,
    ),
    docker_image_bucket_name=GCP_BUCKET,
    job_labels=job_labels,
    stream_logs=True
)

