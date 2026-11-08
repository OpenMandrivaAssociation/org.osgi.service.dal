Name:		org.osgi.service.dal
Version:	1.0.2
Release:	1
Summary:	OSGi Device Abstraction Layer API
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.service.dal/%{version}/org.osgi.service.dal-%{version}-sources.jar
Source1:	https://raw.githubusercontent.com/osgi/osgi/r8-cmpn-final/LICENSE#/org.osgi.service.dal-%{version}-LICENSE

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.osgi:osgi.annotation)
BuildRequires:	mvn(org.osgi:osgi.core)
BuildRequires:	mvn(org.osgi:org.osgi.service.device)
BuildRequires:	mvn(org.osgi:org.osgi.service.event)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
OSGi Device Abstraction Layer 1.0. Devices, functions, and function events.
FunctionEvent extends Event from the packaged Event Admin 1.4.1. Upstream
asked for 1.3.1. Filter, FrameworkUtil, and InvalidSyntaxException come
from OSGi Core. Device category constants are only referenced from
javadoc, so the Device service is provided. The versioning annotation is
provided from osgi.annotation 8.1.0. Upstream asked for framework 1.8.0
and annotation 8.0.1. This build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
cp -p %{SOURCE1} LICENSE
mkdir -p src/main/java
mv org src/main/java/
python - <<'PY'
from pathlib import Path

root = Path("src/main/java/org/osgi/service/dal")
names = sorted(path.name for path in root.glob("*.java"))
expect = [
    "Device.java",
    "DeviceException.java",
    "DevicePermission.java",
    "Function.java",
    "FunctionData.java",
    "FunctionEvent.java",
    "OperationMetadata.java",
    "PropertyMetadata.java",
    "SIUnits.java",
    "package-info.java",
]
if names != expect:
    raise SystemExit("java files " + " ".join(names))
text = (root / "package-info.java").read_text(encoding="utf-8")
if '@Version("1.0.2")' not in text:
    raise SystemExit("package-info version changed")
if list(Path(".").rglob("packageinfo")):
    raise SystemExit("unexpected packageinfo")
if "Apache License" not in Path("LICENSE").read_text(encoding="utf-8"):
    raise SystemExit("LICENSE is not the Apache license")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.service.dal</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:org.osgi.service.dal</name>
  <description>OSGi Device Abstraction Layer.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.core</artifactId>
      <version>6.0.0</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.service.event</artifactId>
      <version>1.4.1</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.service.device</artifactId>
      <version>1.1.0</version>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.annotation</artifactId>
      <version>8.1.0</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>org.osgi.service.dal</artifactId>",
    "<artifactId>osgi.core</artifactId>",
    "<version>6.0.0</version>",
    "<artifactId>org.osgi.service.event</artifactId>",
    "<version>1.4.1</version>",
    "<artifactId>org.osgi.service.device</artifactId>",
    "<version>1.1.0</version>",
    "<artifactId>osgi.annotation</artifactId>",
    "<version>8.1.0</version>",
    "<scope>provided</scope>",
    "<version>%{version}</version>",
    "<release>8</release>",
    "</project.build.sourceEncoding>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "SNAPSHOT", "<source>", "<target>", "<parent>", "felix", "maven-bundle-plugin", "<version>1.3.1</version>", "<version>1.8.0</version>", "<version>8.0.1</version>", "org.osgi.framework", "org.osgi.util.function", "projectbuild.sourceEncoding"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.osgi.service.dal-%{version}.jar --describe-module org.osgi.service.dal > module-describe.txt
grep -q '^org.osgi.service.dal' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }
python - <<'PY'
import zipfile
from pathlib import Path
jar = Path("target/org.osgi.service.dal-%{version}.jar")
with zipfile.ZipFile(jar) as zf:
    names = set(zf.namelist())
required = {
    "org/osgi/service/dal/package-info.class",
    "org/osgi/service/dal/Device.class",
    "org/osgi/service/dal/DeviceException.class",
    "org/osgi/service/dal/DevicePermission.class",
    "org/osgi/service/dal/DevicePermissionCollection.class",
    "org/osgi/service/dal/Function.class",
    "org/osgi/service/dal/FunctionData.class",
    "org/osgi/service/dal/FunctionEvent.class",
    "org/osgi/service/dal/OperationMetadata.class",
    "org/osgi/service/dal/PropertyMetadata.class",
    "org/osgi/service/dal/SIUnits.class",
}
missing = sorted(required - names)
if missing:
    raise SystemExit("missing " + " ".join(missing))
if any(name.endswith("packageinfo") for name in names):
    raise SystemExit("unexpected packageinfo")
PY

%files -f .mfiles
%doc LICENSE
