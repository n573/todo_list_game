@echo off
pushd "%~dp0"
.\gradlew.bat assembleDebug
.\gradlew.bat installDebug
popd