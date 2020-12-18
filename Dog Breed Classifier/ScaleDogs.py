import tensorflow_cloud as tfc

GCP_BUCKET = 'modeldogbreeds'

job_labels = {'job': 'dog_breeds'}

tfc.run(
    entry_point='TrainDogs.py',
    requirements_txt='requirements.txt',
    docker_image_bucket_name=GCP_BUCKET,
    job_labels=job_labels,
)

