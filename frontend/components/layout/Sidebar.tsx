'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { getPrimaryRole, isAdmin, isBloodBankStaff, isDonor, isHospitalStaff } from '@/lib/auth';

type NavItem = { label: string; href: string };

export function Sidebar() {
  const pathname = usePathname();
  const user = useAuthStore((state) => state.user);
  const role = getPrimaryRole(user);
  let title = 'Workspace';
  let items: NavItem[] = [];

  if (isDonor(role)) {
    title = 'Donor workspace';
    items = [
      { label: 'Overview', href: '/donor' },
      { label: 'Donor profile', href: '/donor/profile' },
    ];
  } else if (isHospitalStaff(role)) {
    title = 'Hospital workspace';
    items = [
      { label: 'Overview', href: '/hospital' },
      { label: 'Emergency desk', href: '/hospital/emergency' },
      { label: 'Requisitions', href: '/hospital/requests' },
      { label: 'Facility profile', href: '/hospital/profile' },
    ];
  } else if (isBloodBankStaff(role)) {
    title = 'Blood bank workspace';
    items = [
      { label: 'Overview & inventory', href: '/blood-bank' },
      { label: 'Facility profile', href: '/blood-bank/profile' },
    ];
  } else if (isAdmin(role)) {
    title = 'Administration';
    items = [{ label: 'Operations overview', href: '/admin' }];
  }

  return (
    <nav aria-label={`${title} navigation`} className="dashboard-nav w-full min-w-0 overflow-x-auto border-b border-border bg-card lg:sticky lg:top-16 lg:h-[calc(100vh-4rem)] lg:w-52 lg:shrink-0 lg:overflow-x-visible lg:overflow-y-auto lg:border-b-0 lg:border-r lg:px-3 lg:py-6 xl:w-60 xl:px-4">
      <p className="hidden px-3 pb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground lg:block">
        {title}
      </p>
      <ul className="flex w-max gap-1 px-3 py-2 lg:w-auto lg:flex-col lg:px-0 lg:py-0">
        {items.map((item) => {
          const active = pathname === item.href || (item.href !== '/donor' && item.href !== '/hospital' && item.href !== '/blood-bank' && pathname.startsWith(`${item.href}/`));
          return (
            <li key={item.href} className="shrink-0 lg:w-full">
              <Link
                href={item.href}
                aria-current={active ? 'page' : undefined}
                className={`flex min-h-11 items-center rounded-lg px-3 text-sm font-medium transition-colors ${active ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
              >
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
