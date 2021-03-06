### RPM cms cms-common 1.0
## REVISION 1107
## NOCOMPILER

%define online %(case %cmsplatf in (*onl_*_*) echo true;; (*) echo false;; esac)
%if "%{?cmsroot:set}" != "set"
%define cmsroot       %instroot
%endif

Source: cmsos
Source1: migrate-cvsroot
Source2: cmspm

%prep
#Make sure that we always build cms-common with a different revision and 
#hardcoded version 1.0 because this is what bootstrap.sh is going to install
%if "%v" != "1.0"
  echo "ERROR: Please do not change the version. We have to build this RPM with a different REVISION"
  echo "       Please update the revision in %n.spec and make sure that version is set to 1.0"
  exit 1
%endif

%build

%install

#Create all files in %i/%{pkgrevision} directory.
mkdir -p %i/%{pkgrevision}/common
cd %i/%{pkgrevision}

cp %_sourcedir/cmsos ./common/cmsos
cp %_sourcedir/migrate-cvsroot ./common/migrate-cvsroot
cp %_sourcedir/cmspm ./common/cmspm

%if "%online" != "true"
cat << \EOF_CMSARCH_SH > ./common/cmsarch
#!/bin/sh
osarch=`%instroot/common/cmsos`
compilerv=gcc462
# We need to assume 1 compiler per platform. 
# There is no other way around this.
if [ ! "$SCRAM_ARCH" ]
then
    case $osarch in
        osx104_ia32) compilerv=gcc401;;
        osx104_ppc32) compilerv=gcc400;;
        osx105_*) compilerv=gcc401;;
        osx106_*) compilerv=gcc421;;
        osx107_*) compilerv=gcc462;;
        osx108_*) compilerv=gcc472;;
        slc6_*) compilerv=gcc462; osarch=slc6_amd64;;
        slc5_*) compilerv=gcc462; osarch=slc5_amd64;;
        *) compilerv=gcc462; osarch=slc5_amd64;;
    esac
    echo ${osarch}_${compilerv}
else
    echo $SCRAM_ARCH
fi

EOF_CMSARCH_SH
%else
cat << \EOF_CMSARCH_SH > ./common/cmsarch
#!/bin/sh
if [ ! "$SCRAM_ARCH" ] ; then
    echo %cmsplatf
else
    echo $SCRAM_ARCH
fi

EOF_CMSARCH_SH
%endif

### BASH code

cat << \EOF_CMSSET_DEFAULT_SH > ./cmsset_default.sh
export PATH=%instroot/common:%instroot/bin:$PATH

if [ ! $SCRAM_ARCH ]
then
    SCRAM_ARCH=`%instroot/common/cmsarch`
    export SCRAM_ARCH
fi

here=%{instroot}

if [ "$VO_CMS_SW_DIR" != ""  ] 
then
    here=$VO_CMS_SW_DIR
else
    if [ "$OSG_APP" != "" ]
    then
        here=$OSG_APP/cmssoft/cms
    fi
fi

if [ ! -d $here/${SCRAM_ARCH}/etc/profile.d ] 
then
    echo "Your shell is not able to find where cmsset_default.sh is located." 
    echo "Either you have not set VO_CMS_SW_DIR or OSG_APP correctly"
    echo "or SCRAM_ARCH is not set to a valid architecture."
fi

for pkg in `/bin/ls $here/${SCRAM_ARCH}/etc/profile.d/ | grep 'S.*[.]sh'`
do
	source $here/${SCRAM_ARCH}/etc/profile.d/$pkg
done

if [ ! $CMS_PATH ]
then
    export CMS_PATH=$here
fi

# aliases
alias cmsenv='eval `scramv1 runtime -sh`'
alias cmsrel='scramv1 project CMSSW'

if [ -f $CMS_PATH/SITECONF/local/JobConfig/cmsset_local.sh ]; then
        . $CMS_PATH/SITECONF/local/JobConfig/cmsset_local.sh
fi

if [ ! $CVSROOT ]
then
    CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW
    export CVSROOT
fi

EOF_CMSSET_DEFAULT_SH


### CSH code

cat << \EOF_CMSSET_DEFAULT_CSH > ./cmsset_default.csh

if (${?PATH}) then
    setenv PATH %instroot/common:%instroot/bin:$PATH
else
    setenv PATH %instroot/common:%instroot/bin
endif

if ( ! ${?SCRAM_ARCH}) then
    setenv SCRAM_ARCH `sh -c %instroot/common/cmsarch` 
endif

set here=%instroot 

if ( ${?VO_CMS_SW_DIR} ) then
    set here=$VO_CMS_SW_DIR
else
    # OSG
    if ( ${?OSG_APP} ) then
        set here=$OSG_APP/cmssoft/cms
    endif
    # OSG                       
endif

if ( ! -d $here/${SCRAM_ARCH}/etc/profile.d ) then
    echo "Your shell is not able to find where cmsset_default.csh is located." 
    echo "Either you have not set VO_CMS_SW_DIR or OSG_APP correctly"
    echo "or SCRAM_ARCH is not set to a valid architecture."
endif

foreach pkg ( `/bin/ls ${here}/${SCRAM_ARCH}/etc/profile.d/ | grep 'S.*[.]csh'` )
	source ${here}/${SCRAM_ARCH}/etc/profile.d/$pkg
end
if ( ! ${?CMS_PATH} ) then
    setenv CMS_PATH $here
endif

# aliases
alias cmsenv 'eval `scramv1 runtime -csh`'
alias cmsrel 'scramv1 project CMSSW'

if( -e $CMS_PATH/SITECONF/local/JobConfig/cmsset_local.csh ) then 
        source $CMS_PATH/SITECONF/local/JobConfig/cmsset_local.csh
endif

if ( ! ${?CVSROOT}) then
  setenv CVSROOT :gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW
endif

unset here
EOF_CMSSET_DEFAULT_CSH

cat << \EOF_COMMON_SCRAM > ./common/scram
#!/bin/sh
CMSARCH=`cmsarch`
srbase=%{instroot}/$CMSARCH
sver=$SCRAM_VERSION
dir=`/bin/pwd`
if [ "X${dir}" = "X" ] ; then
  echo "Unable to find current working directory, may be directory was deleted." >&2
  exit 1
fi
while [ ! -d ${dir}/.SCRAM ] && [ "$dir" != "/" ] ; do
  dir=`dirname $dir`
done
if [ "${dir}" != "/" ] && [ -f ${dir}/config/scram_version ] ; then
  sver=`cat ${dir}/config/scram_version`
elif [ "X$sver" = "X" ] ; then
  sver=`cat  ${srbase}/etc/default-scramv1-version`
fi
scram_rel_series=`echo $sver | grep '^V[0-9][0-9]*_[0-9][0-9]*_[0-9][0-9]*' | sed 's|^\(V[0-9][0-9]*_[0-9][0-9]*\)_.*|\1|'`
case $sver in
  V[01]_*|V2_[012]_* ) ;;
  * ) scram_rel_series=`echo $scram_rel_series | sed 's|_.*||'` ;;
esac
if [ "X${scram_rel_series}" != "X" ] && [ -f ${srbase}/etc/default-scram/${scram_rel_series} ] ; then
  sver=`cat ${srbase}/etc/default-scram/${scram_rel_series}`
fi
srbase=%{instroot}/$CMSARCH/lcg/SCRAMV1/${sver}
if [ ! -f ${srbase}/etc/profile.d/init.sh ] ; then
  echo "Unable to find SCRAM version $sver for $CMSARCH architecture."  >&2
  exit 1
fi
. ${srbase}/etc/profile.d/init.sh
${srbase}/bin/scram $@
EOF_COMMON_SCRAM

find . -name "*" -type f | xargs chmod +x 

%post
cd $RPM_INSTALL_PREFIX/%{pkgrel}/%{pkgrevision}
%{relocateCmsFiles} `find . -name "*" -type f`

mkdir -p $RPM_INSTALL_PREFIX/common $RPM_INSTALL_PREFIX/bin $RPM_INSTALL_PREFIX/etc/%{pkgname}  $RPM_INSTALL_PREFIX/%{cmsplatf}/etc/profile.d

#Check if a newer revision is already installed
#Also force installation if older revision has deleted cmsset_default.sh
if [ -f $RPM_INSTALL_PREFIX/cmsset_default.csh ] && [ -f $RPM_INSTALL_PREFIX/etc/%{pkgname}/revision ] ; then
  oldrev=`cat $RPM_INSTALL_PREFIX/etc/%{pkgname}/revision`
  if [ $oldrev -ge %{pkgrevision} ] ; then
    exit 0
  fi
fi

for file in `find . -name "*" -type f`; do
  rm -f $RPM_INSTALL_PREFIX/$file
  cp $file $RPM_INSTALL_PREFIX/$file
done

cd $RPM_INSTALL_PREFIX
rm -f common/scramv1; ln -s scram             common/scramv1
rm -f common/scramv0; ln -s scram             common/scramv0
rm -f bin/cmsarch;    ln -s ../common/cmsarch bin/cmsarch
rm -f bin/cmsos;      ln -s ../common/cmsarch bin/cmsos
rm -f bin/scramv1;    ln -s ../common/scramv1 bin/scramv1
echo %{pkgrevision} > etc/%{pkgname}/revision
