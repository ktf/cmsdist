### RPM external p5-apache-dbi 1.06
## INITENV +PATH PERL5LIB %i/lib/site_perl/%perlversion
%define perlversion %(perl -e 'printf "%%vd", $^V')
%define perlarch %(perl -MConfig -e 'print $Config{archname}')
%define downloadn Apache-DBI

Source: http://search.cpan.org/CPAN/authors/id/P/PG/PGOLLUCCI/%{downloadn}-%{v}.tar.gz

# Fake provides, should be on system.
Provides:  perl(Digest::SHA1)

%prep
%setup -n %downloadn-%v
%build
LC_ALL=C; export LC_ALL
perl Makefile.PL PREFIX=%i LIB=%i/lib/site_perl/%perlversion
make
#
