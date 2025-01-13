import {
  Container,
  Heading,
  SkeletonText,
  Tab,
  Table,
  TableContainer,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createFileRoute,
  useNavigate,
  useSearch,
} from "@tanstack/react-router";
import { useEffect } from "react";
import { z } from "zod";

import { ProjectsService, TasksService } from "../../client/index.ts";
import ActionsMenu from "../../components/Common/ActionsMenu.tsx";
import Navbar from "../../components/Common/Navbar.tsx";
import AddItem from "../../components/Items/AddProject.tsx";
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx";
import "./layout.css";

const itemsSearchSchema = z.object({
  page: z.number().catch(1),
});

export const Route = createFileRoute("/_layout/tasks")({
  component: Tasks,
  validateSearch: (search) => {
    return itemsSearchSchema.parse(search);
  },
});

const PER_PAGE = 5;

function getTasksQueryOptions({ page, id }: { page: number; id?: string }) {
  return {
    queryFn: () =>
      TasksService.readTasks({
        id: id,
        skip: (page - 1) * PER_PAGE,
        limit: PER_PAGE,
      }),
    queryKey: ["project", { page }],
  };
}

function getMembersQueryOptions({ page, id }: { page: number; id: string }) {
  return {
    queryFn: () =>
      ProjectsService.readProjectUsers({
        id: id,
      }),
    queryKey: ["project", { page }],
  };
}

function MembersTable() {
  const searchParam = useSearch({
    strict: false,
  });
  const prjId = searchParam?.id;
  const queryClient = useQueryClient();
  const { page } = Route.useSearch();
  const navigate = useNavigate({ from: Route.fullPath });
  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    });
  const {
    data: members,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getMembersQueryOptions({ page, id: prjId }),
    placeholderData: (prevData) => prevData,
  });

  const hasNextPage = !isPlaceholderData && members?.data?.length === PER_PAGE;
  const hasPreviousPage = page > 1;

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(
        getMembersQueryOptions({ page: page + 1, id: prjId })
      );
    }
  }, [page, queryClient, hasNextPage]);

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Email</Th>
              <Th>Role</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(4).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {members?.data.map((member) => (
                <Tr key={member.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td isTruncated minWidth="150px">
                    {member.full_name}
                  </Td>
                  <Td
                    color={!member.email ? "ui.dim" : "inherit"}
                    isTruncated
                    minWidth="150px"
                  >
                    {member.email || "N/A"}
                  </Td>
                  <Td isTruncated minWidth="150px">
                    {member.role}
                  </Td>
                  <Td>
                    <ActionsMenu type={"Task"} value={member} />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          )}
        </Table>
      </TableContainer>
      <PaginationFooter
        page={page}
        onChangePage={setPage}
        hasNextPage={hasNextPage}
        hasPreviousPage={hasPreviousPage}
      />
    </>
  );
}

function ProjectsTable() {
  const searchParam = useSearch({
    strict: false,
  });
  const prjId = searchParam?.id;
  const queryClient = useQueryClient();
  const { page } = Route.useSearch();
  const navigate = useNavigate({ from: Route.fullPath });
  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    });
  const {
    data: projects,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getTasksQueryOptions({ page, id: prjId }),
    placeholderData: (prevData) => prevData,
  });

  const hasNextPage = !isPlaceholderData && projects?.data.length === PER_PAGE;
  const hasPreviousPage = page > 1;

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(
        getTasksQueryOptions({ page: page + 1, id: prjId })
      );
    }
  }, [page, queryClient, hasNextPage]);

  function formatDate(dateInput: string) {
    const date = new Date(dateInput);
    let formattedDate = date.toUTCString();
    formattedDate = formattedDate.substring(0, formattedDate.length - 7);
    return formattedDate;
  }

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Description</Th>
              <Th>Status</Th>
              <Th>Deadline</Th>
              <Th>Assignee</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(4).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {projects?.data.map((project) => (
                <Tr key={project.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td isTruncated minWidth="150px">
                    {project.name}
                  </Td>
                  <Td
                    color={!project.description ? "ui.dim" : "inherit"}
                    isTruncated
                    minWidth="150px"
                  >
                    {project.description || "N/A"}
                  </Td>
                  <Td isTruncated minWidth="150px">
                    {project.status}
                  </Td>
                  <Td isTruncated minWidth="150px">
                    {formatDate(project.end_date)}
                  </Td>
                  <Td isTruncated minWidth="150px">
                    {project.status}
                  </Td>
                  <Td>
                    <ActionsMenu type={"Task"} value={project} />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          )}
        </Table>
      </TableContainer>
      <PaginationFooter
        page={page}
        onChangePage={setPage}
        hasNextPage={hasNextPage}
        hasPreviousPage={hasPreviousPage}
      />
    </>
  );
}

function Tasks() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Tasks Management
      </Heading>
      <Tabs defaultValue="members">
        <TabList>
          <Tab value="tasks">Tasks</Tab>
          <Tab value="members">Members</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <Navbar type={"Item"} addModalAs={AddItem} />
            <ProjectsTable />
          </TabPanel>
          <TabPanel>
            <Navbar type={"Item"} addModalAs={AddItem} />
            <MembersTable />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Container>
  );
}
