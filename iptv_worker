name: IPTV Worker


on:
schedule:
- cron: "0 */6 * * *" # Her 6 saatte bir
workflow_dispatch:


jobs:
update-iptv:
runs-on: ubuntu-latest


steps:
- name: Repo'yu klonla
uses: actions/checkout@v4


- name: Python kur
uses: actions/setup-python@v4
with:
python-version: "3.11"


- name: Bağımlılıkları yükle
run: |
python -m pip install --upgrade pip
pip install -r requirements.txt


- name: IPTV scripti çalıştır
run: |
python iptv_worker.py


- name: Çıktıları commit ve push
run: |
git config --local user.email "github-actions[bot]@users.noreply.github.com"
git config --local user.name "github-actions[bot]"
git add aktif_porn18_kanallar.* calismayan_porn18_kanallar.*
git commit -m "Otomatik güncelleme $(date +'%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
git push
