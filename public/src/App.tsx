import React, {useEffect, useState} from 'react';
import Login, {requestLogout} from "./components/Login";
import {IUserData} from "./types/IUserData";
import {APP_NAME} from "./index";
import TabGroup, {ITab} from "./components/TabGroup";
import ViewFollowing from "./components/ViewFollowing";
import ViewForYou from "./components/ViewForYou";
import ViewRecent from "./components/ViewRecent";
import ViewPopular from "./components/ViewPopular";
import ViewSearch from "./components/ViewSearch";
import UserProfile from "./components/UserProfile";
import NotificationBell from "./components/NotificationBell";

interface IProps {
  initialUser?: IUserData | null,
  defaultTab?: string; // Label of the default tab
}

interface ITabConfig extends ITab {
  content?: React.JSX.Element;
  generateContent?: () => React.JSX.Element;
}

export const App = ({ initialUser, defaultTab }: IProps) => {
  const [user, setUser] = useState<IUserData | null>(initialUser ?? null);
  const [viewContent, setViewContent] = useState<React.JSX.Element | null>(null);

  if (user === null) {
    return <Login onLoginSuccess={user => void setUser(user)} />;
  } else {
    const cachedComponents: { [key: string]: React.JSX.Element } = {};

    /** Click the user's name */
    const setCachedContent = (key: string, generator: () => React.JSX.Element) => {
      if (key in cachedComponents) {
        setViewContent(cachedComponents[key]);
      } else {
        const content = generator();
        setViewContent(content);
        cachedComponents[key] = content;
      }
    };


    /** Load content */
    const clickUserName = () =>
      setCachedContent("user-profile", () =>
        <UserProfile user={user} />
      );

    const tabs: (ITab & { generateContent: () => React.JSX.Element })[] = [
      {
        label: 'Following',
        generateContent: () => <ViewFollowing user={user} />,
        async onClick() {
          setCachedContent(this.label, this.generateContent);
          return { select: true };
        }
      },
      {
        label: 'For You',
        generateContent: () => <ViewForYou user={user} />,
        async onClick() {
          setCachedContent(this.label, this.generateContent);
          return { select: true };
        }
      },
      {
        label: 'Recent',
        generateContent: () => <ViewRecent user={user} />,
        async onClick() {
          setCachedContent(this.label, this.generateContent);
          return { select: true };
        }
      },
      {
        label: 'Popular',
        generateContent: () => <ViewPopular user={user} />,
        async onClick() {
          setCachedContent(this.label, this.generateContent);
          return { select: true };
        }
      },
      {
        label: 'Search',
        generateContent: () => <ViewSearch user={user} />,
        async onClick() {
          setCachedContent(this.label, this.generateContent);
          return { select: true };
        }
      },
      {
        label: 'Logout',
        generateContent: () => <></>, // Unused
        async onClick() {
          if (await requestLogout()) {
            setUser(null);
          }

          return { select: false };
        }
      }
    ];

    // Load default tab content?
    if (!viewContent && defaultTab) {
      const tab = tabs.find(({ label }) => label === defaultTab);

        if (tab) {
          setCachedContent(tab.label, tab.generateContent);
        }
    }

    return (
      <>
        <header>
          <div>
            <div>
              <span>
                {APP_NAME}
              </span>
            </div>
            <div>
              <span onClick={clickUserName}>
                {user.name}
              </span>
              <NotificationBell user={user} />
            </div>
          </div>
          <TabGroup
            tabs={tabs}
            selected={defaultTab ? tabs.findIndex(tab => tab.label === defaultTab) : undefined}
          />
        </header>
        {viewContent}
      </>
    );
  }
};

export default App;
